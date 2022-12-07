from logging import disable as set_logger, INFO, CRITICAL
from os.path import abspath
from pathlib import Path
from shutil import rmtree
from unittest import TestCase
from urllib.parse import urlencode

import responses

from at import create_app

TEST_DATA_DIR = './tests/data/'
DRAFT_A = 'draft-smoke-signals-00.txt'
DRAFT_B = 'draft-smoke-signals-01.txt'
XML_DRAFT = 'draft-smoke-signals-00.xml'
TEST_UNSUPPORTED_FORMAT = 'draft-smoke-signals-00.odt'
TEST_XML_ERROR = 'draft-smoke-signals-00.error.xml'
TEMPORARY_DATA_DIR = './tests/tmp/'
DT_LATEST_DRAFT_URL = 'https://datatracker.ietf.org/doc/rfcdiff-latest-json'
VALID_API_KEY = 'foobar'
ALLOWED_DOMAINS = ['ietf.org', ]


def get_path(filename):
    '''Returns file path'''
    return ''.join([TEST_DATA_DIR, filename])


class TestApiIddiff(TestCase):
    '''Tests for /api/iddiff end point'''

    def setUp(self):
        # susspress logging messages
        set_logger(CRITICAL)
        # create temporary data dir
        Path(TEMPORARY_DATA_DIR).mkdir(exist_ok=True)

        config = {
                'UPLOAD_DIR': abspath(TEMPORARY_DATA_DIR),
                'REQUIRE_AUTH': False,
                'DT_LATEST_DRAFT_URL': DT_LATEST_DRAFT_URL,
                'ALLOWED_DOMAINS': ALLOWED_DOMAINS}

        self.app = create_app(config)

    def tearDown(self):
        # set logging to INFO
        set_logger(INFO)
        # remove temporary data dir
        rmtree(TEMPORARY_DATA_DIR, ignore_errors=True)

    def test_no_file(self):
        with self.app.test_client() as client:
            with self.app.app_context():
                result = client.post(
                        '/api/iddiff',
                        data={'apikey': VALID_API_KEY})
                json_data = result.get_json()

                self.assertEqual(result.status_code, 400)
                self.assertEqual(json_data['error'], 'No documents to compare')

    def test_get_no_label(self):
        with self.app.test_client() as client:
            with self.app.app_context():
                result = client.get(
                        '/api/iddiff',
                        headers={'X-API-KEY': VALID_API_KEY})
                json_data = result.get_json()

                self.assertEqual(result.status_code, 400)
                self.assertEqual(json_data['error'], 'No documents to compare')

    def test_missing_first_file_name(self):
        with self.app.test_client() as client:
            with self.app.app_context():
                result = client.post(
                        '/api/iddiff',
                        data={
                            'file_1': (
                                open(get_path(DRAFT_A), 'rb'),
                                ''),
                            'file_2': (
                                open(get_path(DRAFT_B), 'rb'),
                                DRAFT_B),
                            'apikey': VALID_API_KEY})
                json_data = result.get_json()

                self.assertEqual(result.status_code, 400)
                self.assertEqual(
                        json_data['error'], 'Filename of first draft missing')

    def test_missing_second_file_name(self):
        with self.app.test_client() as client:
            with self.app.app_context():
                result = client.post(
                        '/api/iddiff',
                        data={
                            'file_1': (
                                open(get_path(DRAFT_A), 'rb'),
                                DRAFT_A),
                            'file_2': (
                                open(get_path(DRAFT_B), 'rb'),
                                ''),
                            'apikey': VALID_API_KEY})
                json_data = result.get_json()

                self.assertEqual(result.status_code, 400)
                self.assertEqual(
                        json_data['error'], 'Filename of second draft missing')

    def test_unsupported_first_file_format(self):
        with self.app.test_client() as client:
            with self.app.app_context():
                result = client.post(
                        '/api/iddiff',
                        data={
                            'file_1': (
                                open(get_path(TEST_UNSUPPORTED_FORMAT), 'rb'),
                                TEST_UNSUPPORTED_FORMAT),
                            'file_2': (
                                open(get_path(DRAFT_A), 'rb'),
                                DRAFT_A),
                            'apikey': VALID_API_KEY})
                json_data = result.get_json()

                self.assertEqual(result.status_code, 400)
                self.assertEqual(
                        json_data['error'],
                        'First file format not supported')

    def test_unsupported_second_file_format(self):
        with self.app.test_client() as client:
            with self.app.app_context():
                result = client.post(
                        '/api/iddiff',
                        data={
                            'file_1': (
                                open(get_path(DRAFT_A), 'rb'),
                                DRAFT_A),
                            'file_2': (
                                open(get_path(TEST_UNSUPPORTED_FORMAT), 'rb'),
                                TEST_UNSUPPORTED_FORMAT),
                            'apikey': VALID_API_KEY})
                json_data = result.get_json()

                self.assertEqual(result.status_code, 400)
                self.assertEqual(
                        json_data['error'],
                        'Second file format not supported')

    def test_first_file_convert_error(self):
        with self.app.test_client() as client:
            with self.app.app_context():
                result = client.post(
                        '/api/iddiff',
                        data={
                            'file_1': (
                                open(get_path(TEST_XML_ERROR), 'rb'),
                                TEST_XML_ERROR),
                            'file_2': (
                                open(get_path(DRAFT_A), 'rb'),
                                DRAFT_A),
                            'apikey': VALID_API_KEY})
                json_data = result.get_json()

                self.assertEqual(result.status_code, 400)
                self.assertTrue(json_data['error'].startswith(
                                    'Error converting first draft to text'))

    def test_second_file_convert_error(self):
        with self.app.test_client() as client:
            with self.app.app_context():
                result = client.post(
                        '/api/iddiff',
                        data={
                            'file_1': (
                                open(get_path(DRAFT_A), 'rb'),
                                DRAFT_A),
                            'file_2': (
                                open(get_path(TEST_XML_ERROR), 'rb'),
                                TEST_XML_ERROR),
                            'apikey': VALID_API_KEY})
                json_data = result.get_json()

                self.assertEqual(result.status_code, 400)
                self.assertTrue(json_data['error'].startswith(
                                    'Error converting second draft to text'))

    def test_iddiff_with_two_files(self):
        with self.app.test_client() as client:
            with self.app.app_context():
                result = client.post(
                        '/api/iddiff',
                        data={
                            'file_1': (
                                open(get_path(DRAFT_A), 'rb'),
                                DRAFT_A),
                            'file_2': (
                                open(get_path(DRAFT_B), 'rb'),
                                DRAFT_B),
                            'apikey': VALID_API_KEY})

                data = result.get_data()

                self.assertEqual(result.status_code, 200)
                self.assertIn(b'<html lang="en">', data)
                self.assertIn(str.encode(DRAFT_A), data)
                self.assertIn(str.encode(DRAFT_B), data)

    def test_iddiff_with_two_labels(self):
        pairs = [
            ('draft-ietf-quic-http-23', 'draft-ietf-quic-http-24'),
            ('draft-ietf-quic-http-23.txt', 'draft-ietf-quic-http-24.txt'),
            ('rfc8226', 'draft-ietf-stir-certificates-18'),
            ('rfc8226.txt', 'draft-ietf-stir-certificates-18.txt')]

        with self.app.test_client() as client:
            with self.app.app_context():
                for (doc_1, doc_2) in pairs:
                    result = client.post(
                            '/api/iddiff',
                            data={
                                'doc_1': doc_1,
                                'doc_2': doc_2,
                                'apikey': VALID_API_KEY})

                    data = result.get_data()

                    self.assertEqual(result.status_code, 200)
                    self.assertIn(b'<html lang="en">', data)
                    self.assertIn(str.encode(doc_1), data)
                    self.assertIn(str.encode(doc_2), data)

    def test_iddiff_get_with_two_labels(self):
        pairs = [
            ('draft-ietf-quic-http-23', 'draft-ietf-quic-http-24'),
            ('draft-ietf-quic-http-23.txt', 'draft-ietf-quic-http-24.txt'),
            ('rfc8226', 'draft-ietf-stir-certificates-18'),
            ('rfc8226.txt', 'draft-ietf-stir-certificates-18.txt')]

        with self.app.test_client() as client:
            with self.app.app_context():
                for (doc_1, doc_2) in pairs:
                    result = client.get(
                            '/api/iddiff?' + urlencode({
                                'doc_1': doc_1,
                                'doc_2': doc_2}),
                            headers={'X-API-KEY': VALID_API_KEY})

                    data = result.get_data()

                    self.assertEqual(result.status_code, 200)
                    self.assertIn(b'<html lang="en">', data)
                    self.assertIn(str.encode(doc_1), data)
                    self.assertIn(str.encode(doc_2), data)

    def test_iddiff_with_one_file(self):
        with self.app.test_client() as client:
            with self.app.app_context():
                draft_name = 'draft-ietf-quic-http-23.txt'

                result = client.post(
                        '/api/iddiff',
                        data={
                            'file_1': (
                                open(get_path(DRAFT_A), 'rb'),
                                draft_name),
                            'apikey': VALID_API_KEY})

                data = result.get_data()

                self.assertEqual(result.status_code, 200)
                self.assertIn(b'<html lang="en">', data)
                self.assertIn(str.encode(draft_name), data)

    def test_iddiff_with_one_label(self):
        labels = [
            'draft-ietf-quic-http',
            'draft-ietf-stir-certificates',
            'draft-ietf-quic-http-23',
            'draft-ietf-quic-http-23.txt',
            'rfc8226',
            'rfc8226.txt']

        with self.app.test_client() as client:
            with self.app.app_context():
                for id in labels:
                    for param in ('doc_1', 'doc_2'):
                        result = client.post(
                                '/api/iddiff',
                                data={
                                    param: id,
                                    'apikey': VALID_API_KEY})

                        data = result.get_data()

                        self.assertEqual(result.status_code, 200)
                        self.assertIn(b'<html lang="en">', data)
                        self.assertIn(b'<td class="lblock">', data)
                        self.assertIn(str.encode(id), data)

    def test_iddiff_get_with_one_label(self):
        labels = [
            'draft-ietf-quic-http-23',
            'draft-ietf-quic-http-23.txt',
            'rfc8226',
            'rfc8226.txt']

        with self.app.test_client() as client:
            with self.app.app_context():
                for id in labels:
                    for param in ('doc_1', 'doc_2'):
                        result = client.get(
                                '/api/iddiff?' + urlencode({param: id}),
                                headers={'X-API-KEY': VALID_API_KEY})

                        data = result.get_data()

                        self.assertEqual(result.status_code, 200)
                        self.assertIn(b'<html lang="en">', data)
                        self.assertIn(str.encode(id), data)

    def test_iddiff_with_label_and_file(self):
        with self.app.test_client() as client:
            with self.app.app_context():
                draft_name = 'draft-ietf-quic-http-23.txt'

                result = client.post(
                        '/api/iddiff',
                        data={
                            'file_1': (
                                open(get_path(DRAFT_A), 'rb'),
                                DRAFT_A),
                            'doc_2': draft_name,
                            'apikey': VALID_API_KEY})

                data = result.get_data()

                self.assertEqual(result.status_code, 200)
                self.assertIn(b'<html lang="en">', data)
                self.assertIn(str.encode(DRAFT_A), data)
                self.assertIn(str.encode(draft_name), data)

    def test_iddiff_with_file_and_label(self):
        with self.app.test_client() as client:
            with self.app.app_context():
                draft_name = 'draft-ietf-quic-http-23.txt'

                result = client.post(
                        '/api/iddiff',
                        data={
                            'doc_1': draft_name,
                            'file_2': (
                                open(get_path(DRAFT_A), 'rb'),
                                DRAFT_A),
                            'apikey': VALID_API_KEY})

                data = result.get_data()

                self.assertEqual(result.status_code, 200)
                self.assertIn(b'<html lang="en">', data)
                self.assertIn(str.encode(draft_name), data)
                self.assertIn(str.encode(DRAFT_A), data)

    def test_iddiff_with_non_text_draft(self):
        with self.app.test_client() as client:
            with self.app.app_context():
                result = client.post(
                        '/api/iddiff',
                        data={
                            'file_1': (
                                open(get_path(XML_DRAFT), 'rb'),
                                XML_DRAFT),
                            'file_2': (
                                open(get_path(XML_DRAFT), 'rb'),
                                XML_DRAFT),
                            'apikey': VALID_API_KEY})

                data = result.get_data()

                self.assertEqual(result.status_code, 200)
                self.assertIn(b'<html lang="en">', data)
                self.assertIn(str.encode(XML_DRAFT.split('.')[0]), data)

    def test_iddiff_with_table_only(self):
        labels = [
            'draft-ietf-quic-http-23',
            'draft-ietf-quic-http-23.txt',
            'rfc8226',
            'rfc8226.txt']

        with self.app.test_client() as client:
            with self.app.app_context():
                for id in labels:
                    result = client.post(
                            '/api/iddiff',
                            data={
                                'doc_1': id,
                                'table': 1,
                                'apikey': VALID_API_KEY})

                    data = result.get_data()

                    self.assertEqual(result.status_code, 200)
                    self.assertNotIn(b'<html lang="en">', data)
                    self.assertIn(b'<table', data)
                    self.assertIn(b'</table>', data)
                    self.assertIn(str.encode(id), data)

    def test_wdiff(self):
        labels = [
            'draft-ietf-quic-http-23',
            'draft-ietf-quic-http-23.txt',
            'rfc8226',
            'rfc8226.txt']

        with self.app.test_client() as client:
            with self.app.app_context():
                for id in labels:
                    result = client.post(
                            '/api/iddiff',
                            data={
                                'doc_1': id,
                                'wdiff': True,
                                'apikey': VALID_API_KEY})

                    data = result.get_data()

                    self.assertEqual(result.status_code, 200)
                    self.assertIn(b'<html lang="en">', data)
                    self.assertIn(b'<pre>', data)
                    self.assertIn(b'</pre>', data)

    def test_chbars(self):
        labels = [
            'draft-ietf-quic-http-23',
            'draft-ietf-quic-http-23.txt']

        with self.app.test_client() as client:
            with self.app.app_context():
                for id in labels:
                    result = client.post(
                            '/api/iddiff',
                            data={
                                'doc_1': id,
                                'chbars': True,
                                'apikey': VALID_API_KEY})

                    data = result.get_data()

                    self.assertEqual(result.status_code, 200)
                    self.assertIn(b'|Intended status: Standards Track', data)

    def test_abdiff(self):
        labels = [
            'draft-ietf-quic-http-23',
            'draft-ietf-quic-http-23.txt']

        with self.app.test_client() as client:
            with self.app.app_context():
                for id in labels:
                    result = client.post(
                            '/api/iddiff',
                            data={
                                'doc_1': id,
                                'abdiff': True,
                                'apikey': VALID_API_KEY})

                    data = result.get_data()

                    self.assertEqual(result.status_code, 200)
                    self.assertIn(b'OLD:', data)
                    self.assertIn(b'NEW:', data)

    def test_iddiff_with_invalid_first_url(self):
        urls = [
            'https://www.rfc-editor.org/rfc/rfc9000.xml',
            'https://www.ietf.org/archive/id/invalid',
            '/etc/password',
            'file:///etc/password']
        with self.app.test_client() as client:
            with self.app.app_context():
                for url in urls:
                    result = client.post(
                                '/api/iddiff',
                                data={
                                    'url_1': url,
                                    'apikey': VALID_API_KEY})
                json_data = result.get_json()

                self.assertEqual(result.status_code, 400)
                self.assertIn('error', json_data)

    def test_iddiff_with_invalid_second_url(self):
        valid = 'https://www.ietf.org/archive/id/draft-iab-xml2rfcv2-02.xml'
        urls = [
            'https://www.rfc-editor.org/rfc/rfc9000.xml',
            'https://www.ietf.org/archive/id/invalid',
            '/etc/password',
            'file:///etc/password']
        with self.app.test_client() as client:
            with self.app.app_context():
                for url in urls:
                    result = client.post(
                                '/api/iddiff',
                                data={
                                    'url_1': valid,
                                    'url_2': url,
                                    'apikey': VALID_API_KEY})
                json_data = result.get_json()

                self.assertEqual(result.status_code, 400)
                self.assertIn('error', json_data)

    def test_iddiff_with_one_url(self):
        valid = 'https://www.ietf.org/archive/id/draft-iab-xml2rfcv2-02.xml'
        id = 'draft-iab-xml2rfcv2-02'

        with self.app.test_client() as client:
            with self.app.app_context():
                for param in ('url_1', 'url_2'):
                    result = client.post(
                                '/api/iddiff',
                                data={
                                    param: valid,
                                    'apikey': VALID_API_KEY})

                    data = result.get_data()

                    self.assertEqual(result.status_code, 200)
                    self.assertIn(b'<html lang="en">', data)
                    self.assertIn(str.encode(id), data)

    def test_iddiff_get_with_one_url(self):
        valid = 'https://www.ietf.org/archive/id/draft-iab-xml2rfcv2-02.xml'
        id = 'draft-iab-xml2rfcv2-02'

        with self.app.test_client() as client:
            with self.app.app_context():
                for param in ('url_1', 'url_2'):
                    result = client.get(
                                '/api/iddiff?' + urlencode({param: valid}),
                                headers={'X-API-KEY': VALID_API_KEY})

                    data = result.get_data()

                    self.assertEqual(result.status_code, 200)
                    self.assertIn(b'<html lang="en">', data)
                    self.assertIn(str.encode(id), data)

    def test_iddiff_with_two_urls(self):
        url_1 = 'https://www.ietf.org/archive/id/draft-iab-xml2rfcv2-01.xml'
        url_2 = 'https://www.ietf.org/archive/id/draft-iab-xml2rfcv2-02.xml'
        doc_1 = 'draft-iab-xml2rfcv2-01'
        doc_2 = 'draft-iab-xml2rfcv2-01'

        with self.app.test_client() as client:
            with self.app.app_context():
                result = client.post(
                            '/api/iddiff',
                            data={
                                'url_1': url_1,
                                'url_2': url_2,
                                'apikey': VALID_API_KEY})

                data = result.get_data()

                self.assertEqual(result.status_code, 200)
                self.assertIn(b'<html lang="en">', data)
                self.assertIn(str.encode(doc_1), data)
                self.assertIn(str.encode(doc_2), data)

    def test_iddiff_get_with_two_urls(self):
        url_1 = 'https://www.ietf.org/archive/id/draft-iab-xml2rfcv2-01.xml'
        url_2 = 'https://www.ietf.org/archive/id/draft-iab-xml2rfcv2-02.xml'
        doc_1 = 'draft-iab-xml2rfcv2-01'
        doc_2 = 'draft-iab-xml2rfcv2-01'

        with self.app.test_client() as client:
            with self.app.app_context():
                result = client.get(
                            '/api/iddiff?' + urlencode({
                                'url_1': url_1,
                                'url_2': url_2}),
                            headers={'X-API-KEY': VALID_API_KEY})

                data = result.get_data()

                self.assertEqual(result.status_code, 200)
                self.assertIn(b'<html lang="en">', data)
                self.assertIn(str.encode(doc_1), data)
                self.assertIn(str.encode(doc_2), data)

    def test_iddiff_rfcdiff_compatibility_url(self):
        valid = 'https://www.ietf.org/archive/id/draft-iab-xml2rfcv2-02.xml'
        id = 'draft-iab-xml2rfcv2-02'

        with self.app.test_client() as client:
            with self.app.app_context():
                for param in ('url1', 'url2'):
                    result = client.get(
                                '/api/iddiff?' + urlencode({param: valid}),
                                headers={'X-API-KEY': VALID_API_KEY})

                    data = result.get_data()

                    self.assertEqual(result.status_code, 200)
                    self.assertIn(b'<html lang="en">', data)
                    self.assertIn(str.encode(id), data)

    def test_iddiff_rfcdiff_compatibility_docname(self):
        labels = [
            'draft-ietf-quic-http-23',
            'draft-ietf-quic-http-23.txt',
            'rfc8226',
            'rfc8226.txt']

        with self.app.test_client() as client:
            with self.app.app_context():
                for id in labels:
                    for param in ('url1', 'url2'):
                        result = client.get(
                                '/api/iddiff?' + urlencode({param: id}),
                                headers={'X-API-KEY': VALID_API_KEY})

                        data = result.get_data()

                        self.assertEqual(result.status_code, 200)
                        self.assertIn(b'<html lang="en">', data)
                        self.assertIn(str.encode(id), data)

    def test_wdiff_rfcdiff_compatibility(self):
        labels = [
            'https://www.ietf.org/archive/id/draft-iab-xml2rfcv2-02.xml',
            'draft-ietf-quic-http-23',
            'draft-ietf-quic-http-23.txt',
            'rfc8226',
            'rfc8226.txt']

        with self.app.test_client() as client:
            with self.app.app_context():
                for id in labels:
                    result = client.get(
                            '/api/iddiff?' + urlencode({
                                'url1': id,
                                'difftype': '--hwdiff'}),
                            headers={'X-API-KEY': VALID_API_KEY})

                    data = result.get_data()

                    self.assertEqual(result.status_code, 200)
                    self.assertIn(b'<html lang="en">', data)
                    self.assertIn(b'<pre>', data)
                    self.assertIn(b'</pre>', data)

    def test_chbars_rfcdiff_compatibility(self):
        labels = [
            'draft-ietf-quic-http-23',
            'draft-ietf-quic-http-23.txt']

        with self.app.test_client() as client:
            with self.app.app_context():
                for id in labels:
                    result = client.get(
                            '/api/iddiff?' + urlencode({
                                'url1': id,
                                'difftype': '--chbars'}),
                            headers={'X-API-KEY': VALID_API_KEY})

                    data = result.get_data()

                    self.assertEqual(result.status_code, 200)
                    self.assertIn(b'|Intended status: Standards Track', data)

    def test_abdiff_rfcdiff_compatibility(self):
        labels = [
            'draft-ietf-quic-http-23',
            'draft-ietf-quic-http-23.txt']

        with self.app.test_client() as client:
            with self.app.app_context():
                for id in labels:
                    result = client.get(
                            '/api/iddiff?' + urlencode({
                                'url1': id,
                                'difftype': '--abdiff'}),
                            headers={'X-API-KEY': VALID_API_KEY})

                    data = result.get_data()

                    self.assertEqual(result.status_code, 200)
                    self.assertIn(b'OLD:', data)
                    self.assertIn(b'NEW:', data)

    @responses.activate
    def test_error_document_not_found(self):
        rfc = 'rfc666'
        responses.add(
                responses.GET,
                '/'.join([DT_LATEST_DRAFT_URL, rfc]),
                json={},
                status=200)
        with self.app.test_client() as client:
            with self.app.app_context():
                result = client.get(
                        '/api/iddiff?' + urlencode({'doc_1': rfc}),
                        headers={'X-API-KEY': VALID_API_KEY})
                json_data = result.get_json()

                self.assertEqual(result.status_code, 400)
                msg = 'Can not find url for the latest document on datatracker'
                self.assertEqual(json_data['error'], msg)

    @responses.activate
    def test_error_document_2_not_found(self):
        url_1 = 'https://www.ietf.org/archive/id/draft-ietf-quic-http-23.txt'
        rfc = 'rfc666'
        responses.add(
                responses.GET,
                '/'.join([DT_LATEST_DRAFT_URL, rfc]),
                json={},
                status=200)
        responses.add(
                responses.GET,
                url_1,
                status=200)
        with self.app.test_client() as client:
            with self.app.app_context():
                result = client.get(
                        '/api/iddiff?' + urlencode({
                            'url_1': url_1, 'doc_2': rfc}),
                        headers={'X-API-KEY': VALID_API_KEY})
                json_data = result.get_json()

                self.assertEqual(result.status_code, 400)
                msg = 'Can not find url for the latest document on datatracker'
                self.assertEqual(json_data['error'], msg)

    @responses.activate
    def test_error_document_2_not_found_without_doc_2(self):
        draft_1 = 'draft-ietf-quic-http-23'
        draft_2 = 'draft-ietf-quic-http-22'
        url_1 = 'https://www.ietf.org/archive/id/draft-ietf-quic-http-23.txt'
        dt_response = {'previous': draft_2}
        responses.add(
                responses.GET,
                '/'.join([DT_LATEST_DRAFT_URL, draft_1]),
                json=dt_response,
                status=200)
        responses.add(
                responses.GET,
                '/'.join([DT_LATEST_DRAFT_URL, draft_2]),
                json={},
                status=200)
        responses.add(
                responses.GET,
                url_1,
                status=200)
        with self.app.test_client() as client:
            with self.app.app_context():
                result = client.get(
                        '/api/iddiff?' + urlencode({'url_1': url_1}),
                        headers={'X-API-KEY': VALID_API_KEY})
                json_data = result.get_json()

                self.assertEqual(result.status_code, 400)
                msg = 'Can not find url for the latest document on datatracker'
                self.assertEqual(json_data['error'], msg)

    @responses.activate
    def test_error_document_download_error(self):
        rfc = 'rfc9000'
        rfc_url = 'https://example.com/rfc9000.txt'
        dt_response = {'content_url': rfc_url, 'name': rfc}
        responses.add(
                responses.GET,
                '/'.join([DT_LATEST_DRAFT_URL, rfc]),
                json=dt_response,
                status=200)
        responses.add(
                responses.GET,
                rfc_url,
                status=404)

        with self.app.test_client() as client:
            with self.app.app_context():
                result = client.get(
                        '/api/iddiff?' + urlencode({'doc_1': rfc}),
                        headers={'X-API-KEY': VALID_API_KEY})
                json_data = result.get_json()

                self.assertEqual(result.status_code, 400)
                msg = 'Error occured while downloading file.'
                self.assertEqual(json_data['error'], msg)

    @responses.activate
    def test_error_document_2_download_error_without_doc_2(self):
        draft_1 = 'draft-ietf-quic-http-23'
        draft_2 = 'draft-ietf-quic-http-22'
        url_1 = 'https://www.ietf.org/archive/id/draft-ietf-quic-http-23.txt'
        url_2 = 'https://www.ietf.org/archive/id/draft-ietf-quic-http-22.txt'
        dt_response_1 = {'previous': draft_2}
        dt_response_2 = {'content_url': url_2, 'name': draft_2}
        responses.add(
                responses.GET,
                '/'.join([DT_LATEST_DRAFT_URL, draft_1]),
                json=dt_response_1,
                status=200)
        responses.add(
                responses.GET,
                '/'.join([DT_LATEST_DRAFT_URL, draft_2]),
                json=dt_response_2,
                status=200)
        responses.add(
                responses.GET,
                url_1,
                status=200)
        responses.add(
                responses.GET,
                url_2,
                status=404)
        with self.app.test_client() as client:
            with self.app.app_context():
                result = client.get(
                        '/api/iddiff?' + urlencode({'url_1': url_1}),
                        headers={'X-API-KEY': VALID_API_KEY})
                json_data = result.get_json()

                self.assertEqual(result.status_code, 400)
                msg = 'Error occured while downloading file.'
                self.assertEqual(json_data['error'], msg)

    @responses.activate
    def test_error_document_2_download_error(self):
        url_1 = 'https://www.ietf.org/archive/id/draft-ietf-quic-http-23.txt'
        rfc = 'rfc9000'
        rfc_url = 'https://example.com/rfc9000.txt'
        dt_response = {'content_url': rfc_url, 'name': rfc}
        responses.add(
                responses.GET,
                '/'.join([DT_LATEST_DRAFT_URL, rfc]),
                json=dt_response,
                status=200)
        responses.add(
                responses.GET,
                rfc_url,
                status=404)
        responses.add(
                responses.GET,
                url_1,
                status=200)

        with self.app.test_client() as client:
            with self.app.app_context():
                result = client.get(
                        '/api/iddiff?' + urlencode({
                            'url_1': url_1, 'doc_2': rfc}),
                        headers={'X-API-KEY': VALID_API_KEY})
                json_data = result.get_json()

                self.assertEqual(result.status_code, 400)
                msg = 'Error occured while downloading file.'
                self.assertEqual(json_data['error'], msg)

    def test_error_draft_name_error(self):
        with self.app.test_client() as client:
            with self.app.app_context():
                result = client.post(
                        '/api/iddiff',
                        data={
                            'file_1': (
                                open(get_path(DRAFT_A), 'rb'),
                                'test-foobar.txt'),
                            'apikey': VALID_API_KEY})
                json_data = result.get_json()

                self.assertEqual(result.status_code, 400)
                msg = 'Can not determine draft/rfc'
                self.assertEqual(json_data['error'], msg)

    def test_iddiff_with_latest(self):
        with self.app.test_client() as client:
            with self.app.app_context():
                id = 'draft-ietf-quic-http'
                result = client.post(
                        '/api/iddiff',
                        data={
                            'doc_1': id,
                            'latest': True,
                            'apikey': VALID_API_KEY})

                data = result.get_data()
                self.assertEqual(result.status_code, 200)
                self.assertIn(b'<html lang="en">', data)
