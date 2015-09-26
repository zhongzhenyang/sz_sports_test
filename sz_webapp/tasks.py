# coding:utf-8

from celery.utils.log import get_task_logger

from flask import current_app
import datetime
import smtplib
import socket
from .factory import create_celery_app
from .core import db, get_model
from . import qinius

logger = get_task_logger(__name__)
celery_app = create_celery_app()


@celery_app.task(bind=True)
def send_email(self, recipient, subject, html_message, text_message):
    mail_engine = current_app.extensions.get('mail', None)
    if not mail_engine:
        logger.error(
            'Flask-Mail has not been initialized. Initialize Flask-Mail or disable USER_SEND_PASSWORD_CHANGED_EMAIL, USER_SEND_REGISTERED_EMAIL and USER_SEND_USERNAME_CHANGED_EMAIL')
        return

    from flask_mail import Message

    try:

        # Construct Flash-Mail message
        message = Message(subject, recipients=[recipient], html=html_message, body=text_message)
        mail_engine.send(message)

    # Print helpful error messages on exceptions
    except (socket.gaierror, socket.error) as e:
        logger.error('SMTP Connection error: Check your MAIL_HOSTNAME or MAIL_PORT settings.', e)
    except smtplib.SMTPAuthenticationError:
        logger.error('SMTP Authentication error: Check your MAIL_USERNAME and MAIL_PASSWORD settings.')
    except Exception as exc:
        logger.error("send_email error", exc)
        raise self.retry(exc=exc)


@celery_app.task(bind=True)
def set_competition_status(self, competition_id, status):
    from .models import Competition

    competition = db.session.query(Competition).get(competition_id)
    if competition:
        today = datetime.date.today()
        if today == competition.date_reg_end:
            competition.status = status
            db.session.add(competition)


@celery_app.task(bind=True)
def thumbnail_highlight_with_width(self, match_highlight_uid, new_width=200):
    """
        指定目标图片宽度后高度等比缩放

    """
    from .models import MatchHighlight

    match_highlights = MatchHighlight.query.filter(MatchHighlight.uid == match_highlight_uid).all()
    if match_highlights and 'image' in match_highlights[0].details:
        image_url = match_highlights[0].details.get('image')
        image_info = qinius.get_image_info(image_url)
        if image_info and 'height' in image_info and 'width' in image_info:
            try:
                height = image_info['height']
                width = image_info['width']
                new_height = new_width * height / width
                new_size = '%dx%d' % (new_width, new_height)
                qinius.mk_image_thumbnail(key_or_url=image_url, image_sizes=[new_size])
                last_dot = image_url.rindex('.')
                new_image_url = '%(prefix)s-%(image_size)s%(suffix)s' % {"prefix": image_url[:last_dot],
                                                                         "image_size": new_size,
                                                                         "suffix": image_url[last_dot:]}
                details = {'image': new_image_url, 'width': new_width, 'height': new_height}
                for match_highlight in match_highlights:
                    match_highlight.details = details
                    match_highlight.status = -2
                    db.session.add(match_highlight)
                db.session.commit()
            except Exception as exc:
                logger.error("thumbnail_highlight_with_width error, match_highlight_uid:" + match_highlight_uid, exc)
                raise self.retry(exc=exc)


@celery_app.task(bind=True)
def thumbnail_image(self, model_name, model_id, prop_name, image, new_size):
    model = get_model(model_name)

    try:
        qinius.mk_image_thumbnail(key_or_url=image, image_sizes=[new_size])
        last_dot = image.rindex('.')
        new_image = '%(prefix)s-%(image_size)s%(suffix)s' % {"prefix": image[:last_dot], "image_size": new_size,
                                                             "suffix": image[last_dot:]}

        model_instance = db.session.query(model).get(model_id)
        if model_instance is not None and getattr(model_instance, prop_name, None) == image:
            setattr(model_instance, prop_name, new_image)
            db.session.add(model_instance)

        db.session.commit()
    except Exception as exc:
        logger.error("thumbnail_image error, model_name:%s, model_id:%d, prop_name:%s, image:%s" % (model_name, model_id, prop_name, image), exc)
        raise self.retry(exc=exc)
