# -*- coding: utf-8 -*-
import hashlib
import urlparse
import logging
_logger = logging.getLogger(__name__)

try:
    import boto3
except:
    _logger.debug('boto3 package is required which is not \
    found on your installation')

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.safe_eval import safe_eval


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    def _get_bucket_name(self):
        return self.env['ir.config_parameter'].get_param('s3.bucket')

    def _get_condition(self):
        return self.env['ir.config_parameter'].get_param('s3.condition')

    def _get_access_key_id(self):
        return self.env['ir.config_parameter'].get_param('s3.access_key_id')

    def _get_secret_key(self):
        return self.env['ir.config_parameter'].get_param('s3.secret_key')

    @api.model
    def _get_s3_object_url(self, s3, s3_bucket_name, key_name):
        bucket_location = s3.meta.client.get_bucket_location(Bucket=s3_bucket_name)
        object_url = "https://s3-{0}.amazonaws.com/{1}/{2}".format(
            bucket_location['LocationConstraint'],
            s3_bucket_name,
            key_name)
        return object_url

    @api.model
    def _get_s3_resource(self):
        access_key_id = self._get_access_key_id()
        secret_key = self._get_secret_key()

        if not access_key_id or not secret_key:
            raise ValidationError(_('AmazonS3 access_key_id and secret_access_key must be defined in the [Settiings > Parameters > System Parameters]'))

        s3 = boto3.resource(
                's3',
                aws_access_key_id=access_key_id,
                aws_secret_access_key=secret_key,
                )
        bucket_name = self._get_bucket_name()
        bucket = s3.Bucket(bucket_name)
        if not bucket:
            s3.create_bucket(Bucket=bucket_name)
        return s3

    def _inverse_datas(self):
        condition = self._get_condition()
        s3_records = self.filtered(lambda r: safe_eval(condition, {}, {'attachment': r}, mode="eval"))
        for attach in s3_records:
            value = attach.datas
            bin_data = value and value.decode('base64') or ''
            fname = hashlib.sha1(bin_data).hexdigest()

            s3 = self._get_s3_resource()
            bucket_name = self._get_bucket_name()
            s3.Bucket(bucket_name).put_object(
                    Key=fname,
                    Body=bin_data,
                    ACL='public-read',
                    ContentType=attach.mimetype,
                    )

            vals = {
                'file_size': len(bin_data),
                'checksum': self._compute_checksum(bin_data),
                'index_content': self._index(bin_data, attach.datas_fname, attach.mimetype),
                'store_fname': fname,
                'db_datas': False,
                'type': 'url',
                'url': self._get_s3_object_url(s3, bucket_name, fname),
            }
            super(IrAttachment, attach.sudo()).write(vals)

        super(IrAttachment, self - s3_records)._inverse_datas()
