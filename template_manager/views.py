from flask import request, render_template, session, send_from_directory
import json
from flask_security import login_required
from flask_login import current_user

import os
import datetime
import tempfile

basefolder = os.path.dirname(__file__)

from hydra_base.lib.objects import JSONObject 
from hydra_base.db import commit_transaction

import hwi.hydrautils.attr_utilities as attrutils
import hwi.hydrautils.template_utilities as tmplutils

from . import templatemanager

from hwi import app, db, db_connection,\
                    get_shadow_attributes,\
                    save_shadow_attributes,\
                    get_quick_attributes,\
                    save_quick_attributes

@templatemanager.route('/templates', methods=['GET'])
@db_connection
@login_required
def go_templates():
    user_id = session['hydra_user_id']
    all_templates = tmplutils.get_all_templates(user_id)
    return render_template('template_manager/templates.html', templates=all_templates)

@templatemanager.route('/get_templates', methods=['GET'])
@db_connection
@login_required
def do_get_all_templates():
    user_id = session['hydra_user_id']
    all_templates = tmplutils.get_all_templates(user_id)
    return all_templates

@templatemanager.route('/newtemplate', methods=['GET'])
@db_connection
@login_required
def go_new_template():

    all_attributes = attrutils.get_all_attributes()

    attr_id_name_lookup = dict([(a.attr_id, a.attr_name) for a in all_attributes])
    attr_dimen_lookup = dict([(a.attr_id, a.attr_dimen) for a in all_attributes])
    return render_template('template_manager/template.html',
                              new=True,
                              all_attrs=all_attributes,
                              attr_id_name_lookup=attr_id_name_lookup,
                              attr_id_name_map=json.dumps(attr_id_name_lookup),#For the javascript
                              attr_dimen_lookup=attr_dimen_lookup,
                              typeattr_lookup={},
                              shadow_attributes = [],
                              shadow_attribute_ids = [],
                              quick_attributes = [],
                              quick_attribute_ids = [],
                          )

@templatemanager.route('/template/<template_id>', methods=['GET'])
@db_connection
@login_required
def go_template(template_id):

    user_id = session['hydra_user_id']
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

    shadow_attributes = get_shadow_attributes(template_id)
    shadow_attribute_ids = [a.attr_id for a in shadow_attributes]
    quick_attributes  = get_quick_attributes(template_id)
    quick_attribute_ids  = [a.attr_id for a in quick_attributes] 

    return render_template('template_manager/template.html',
                           new=False,
                           all_attrs=all_attributes,
                           attr_id_name_lookup=attr_id_name_lookup,
                           attr_id_name_map=json.dumps(attr_id_name_lookup),#For the javascript
                           template=tmpl,
                           attr_dimen_lookup=attr_dimen_lookup,
                           shadow_attributes = shadow_attributes,
                           shadow_attribute_ids = shadow_attribute_ids,
                           quick_attributes = quick_attributes,
                           quick_attribute_ids = quick_attribute_ids,
                           typeattr_lookup=typeattr_lookup)

@templatemanager.route('/create_template', methods=['POST'])
@db_connection
@login_required
def do_create_template():

    user_id = session['hydra_user_id']

    d = json.loads(request.get_data())

    template_j = JSONObject(d)

    newtemplate = tmplutils.create_template(template_j, user_id)

    commit_transaction()

    return newtemplate.as_json()


@templatemanager.route('/load_template', methods=['POST'])
@db_connection
@login_required
def do_load_template():

    now = datetime.datetime.now().strftime("%y%m%d%H%M")

    template_folder = app.config.get('TEMPLATE_FOLDER', tempfile.gettempdir())
    
    basefolder = os.path.dirname(os.path.join(template_folder, now))

    if not os.path.exists(basefolder):
        os.mkdir(basefolder)

    user_id = session['hydra_user_id']

    template_file = request.files['template_file']
    format = request.values['format']

    template_file.save(os.path.join(basefolder, template_file.filename))

    f = open(os.path.join(basefolder, template_file.filename))
    f_arr = f.readlines()
    text = ''.join(f_arr)

    newtemplate = tmplutils.load_template(text, format, user_id)

    commit_transaction()

    return newtemplate.as_json()

@templatemanager.route('/update_template', methods=['POST'])
@db_connection
@login_required
def do_update_template():

    user_id = session['hydra_user_id']
    
    d = json.loads(request.get_data())

    template_j = JSONObject(d)

    newtemplate = tmplutils.update_template(template_j, user_id)

    save_quick_attributes(newtemplate.template_id, template_j.quick_attributes)
    save_shadow_attributes(newtemplate.template_id, template_j.shadow_attributes)

    commit_transaction()

    db.session.commit()

    return newtemplate.as_json()

@templatemanager.route('/delete_template', methods=['POST'])
@db_connection
@login_required
def do_delete_template(template_id):

    user_id = session['hydra_user_id']

    status = tmplutils.delete_template(template_id, user_id)

    commit_transaction()

    return status


@templatemanager.route('/delete_type', methods=['POST'])
@db_connection
@login_required
def do_delete_type(type_id):
    user_id = session['hydra_user_id']

    status = tmplutils.delete_type(type_id, user_id)

    commit_transaction()

    return status


@templatemanager.route('/downloadtemplate/<template_id>/<format>', methods=['GET'])
@templatemanager.route('/downloadtemplate/', methods=['GET'])
@db_connection
@login_required
def do_download_template(template_id, format):
    """
        Get a template as a file in the specified format.
        if no format is given, the template will be returned by default in xml
    """
    if format is None or format.lower() == 'json':
        return _get_template_as_json(template_id)
    elif format.lower() == 'xml':
        return _get_template_as_xml(template_id)

def _get_template_as_json(template_id):
    user_id = session['hydra_user_id']

    template_dict  = tmplutils.get_template_as_dict(template_id, user_id)

    tmpfolder = os.tempnam()
    os.mkdir(tmpfolder)
    outputname = '%s.json'%(template_dict['template'].name)
    location = os.path.join(tmpfolder, outputname)

    with open(location, 'w') as f:
        f.write(json.dumps(template_dict))

    app.logger.info("File export complete.")
    
    return send_from_directory(tmpfolder, outputname, as_attachment=True)

def _get_template_as_xml(template_id):
    user_id = session['hydra_user_id']

    template_j = tmplutils.get_template(template_id, user_id)

    template_xml_string = tmplutils.get_template_as_xml(template_id, user_id)

    tmpfolder = os.tempnam()
    os.mkdir(tmpfolder)
    outputname = '%s.xml'%(template_j.name)
    location = os.path.join(tmpfolder, outputname)

    with open(location, 'w') as f:
        f.write(template_xml_string)

    app.logger.info("File export complete.")
    
    return send_from_directory(tmpfolder, outputname, as_attachment=True)
