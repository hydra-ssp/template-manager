from flask import  request, session, redirect, url_for, escape, send_file, jsonify, Markup
import json

from hydra_base.exceptions import HydraError, PermissionError, ResourceNotFoundError

from hydra_base.util.hydra_dateutil import ordinal_to_timestamp

from flask import render_template

from werkzeug import secure_filename
import zipfile
import os
import sys
import datetime
import urllib2

basefolder = os.path.dirname(__file__)

from hydra_base.lib.objects import JSONObject, ResourceScenario
from hydra_base.db import commit_transaction, rollback_transaction, DBSession

import hwi.hydrautils.attr_utilities as attrutils
import hwi.hydrautils.template_utilities as tmplutils
import hwi.hydrautils.dataset_utilities as datasetutils

from . import templatemanager

from hwi import app, requires_login

@templatemanager.route('/templates', methods=['GET'])
@requires_login
def go_templates():
    user_id = request.environ['beaker.session']['user_id']
    all_templates = tmplutils.get_all_templates(user_id)
    return render_template('template_manager/templates.html', templates=all_templates)

@templatemanager.route('/get_templates', methods=['GET'])
@requires_login
def do_get_all_templates():
    user_id = request.environ['beaker.session']['user_id']
    all_templates = tmplutils.get_all_templates(user_id)
    return all_templates

@templatemanager.route('/newtemplate', methods=['GET'])
@requires_login
def go_new_template():
    all_attributes = attrutils.get_all_attributes()
    return render_template('template_manager/template.html',
                                new=True,
                              all_attrs=all_attributes,
                          )

@templatemanager.route('/template/<template_id>', methods=['GET'])
@requires_login
def go_template(template_id):

    user_id = request.environ['beaker.session']['user_id']
    all_attributes = attrutils.get_all_attributes()
    tmpl = tmplutils.get_template(template_id, user_id)

    typeattr_lookup = {}

    for rt in tmpl.templatetypes:
        if rt.typeattrs is not None:
            typeattr_lookup[rt.type_id] = [ta.attr_id for ta in rt.typeattrs]
        else:
            typeattr_lookup[rt.type_id] = []

    attr_id_name_lookup = dict([(a.attr_id, a.attr_name) for a in all_attributes])
    attr_dimen_lookup = dict([(a.attr_id, a.attr_dimen) for a in all_attributes])

    app.logger.info(tmpl)
    return render_template('template_manager/template.html',
                           new=False,
                           all_attrs=all_attributes,
                           attr_id_name_lookup=attr_id_name_lookup,
                           template=tmpl,
                           attr_dimen_lookup=attr_dimen_lookup,
                            typeattr_lookup=typeattr_lookup)

@templatemanager.route('/create_template', methods=['POST'])
@requires_login
def do_create_template():

    user_id = request.environ['beaker.session']['user_id']

    d = json.loads(request.get_data())

    template_j = JSONObject(d)

    newtemplate = tmplutils.create_template(template_j, user_id)

    commit_transaction()

    return newtemplate.as_json()


@templatemanager.route('/load_template', methods=['POST'])
@requires_login
def do_load_template():

    now = datetime.datetime.now().strftime("%y%m%d%H%M")

    basefolder = os.path.join(os.path.dirname(os.path.realpath(__file__)), TEMPLATE_FOLDER, now)
    if not os.path.exists(basefolder):
        os.mkdir(basefolder)

    user_id = request.environ['beaker.session']['user_id']

    template_file = request.files['import_file']

    template_file.save(os.path.join(basefolder, template_file.filename))

    f = open(os.path.join(basefolder, template_file.filename))
    f_arr = f.readlines()
    text = ''.join(f_arr)

    newtemplate = tmplutils.load_template(text, user_id)

    commit_transaction()

    return newtemplate.as_json()

@templatemanager.route('/update_template', methods=['POST'])
@requires_login
def do_update_template():

    user_id = request.environ['beaker.session']['user_id']

    d = json.loads(request.get_data())

    template_j = JSONObject(d)

    newtemplate = tmplutils.update_template(template_j, user_id)

    commit_transaction()

    return newtemplate.as_json()

@templatemanager.route('/delete_template', methods=['POST'])
@requires_login
def do_delete_template(template_id):

    user_id = request.environ['beaker.session']['user_id']

    status = delete_template(template_id, user_id)

    commit_transaction()

    return status
