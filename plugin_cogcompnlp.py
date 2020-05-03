#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json, requests

from os import path

from deepnlpf.core.boost import Boost
from deepnlpf.core.iplugin import IPlugin
from deepnlpf.core.output_format import OutputFormat

class Plugin(IPlugin):

    def __init__(self, id_pool, lang, document, pipeline, online=True):

        if online is False:
            self.start_server_local()

        self._document = document
        self._pipeline = pipeline
        self._id_pool = id_pool

        self.path = path.abspath(path.dirname(__file__)) + 'resources'

        self.IP = "http://macniece.seas.upenn.edu"
        self.PORT = "4001"

        self.service_view_names = self.IP + ':' + self.PORT + '/viewNames'
        self.service_annotate = self.IP + ':' + self.PORT + '/annotate'

        self.headers = {'accept': 'application/json', }

    def run(self):
        annotation = Boost().multithreading(self.annotate_online, self._document['sentences'])
        return self.out_format(annotation)

    def wrapper(self):
        pass

    def start_server_local(self):
        import subprocess
        subprocess.call('cd ' + self.path +
                        ' && pipeline/scripts/runWebserver.sh --port {}'.format(self.PORT), shell=True)

    def annotate_offline(self, text):
        params = {
            'text': '"' + text + '"',
            'views': ', '.join(self._pipeline)
        }
        response = requests.get(self.service_annotate,
                                headers=self.headers, params=params)
        return response.text

    def annotate_online(self, sentence):
        server_url = "http://macniece.seas.upenn.edu:4001/annotate"
        params = {'text': '"' + sentence + '"',
                  'views': ', '.join(self._pipeline)}
        valid = False

        while not valid:
            try:
                response = requests.get(server_url, headers=self.headers, params=params)
                valid = True
                return response.json()
                # print 'URL: ', response.url
            except Exception as err:
                return "Null"
                #log.logging.error("CogComp Exception occurred: "+_sent, exc_info=True)

    def out_format(self, annotation):
        return OutputFormat().doc_annotation(
            _id_pool=self._id_pool,
            _id_dataset=self._document['_id_dataset'], 
            _id_document=self._document['_id'],
            tool="cogcomp",
            annotation=annotation
        )
