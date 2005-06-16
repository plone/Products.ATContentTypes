var _registry = new Object();
var _all_keys = new Array();
var _master_elements = new Object();

function getInputElementToModify(form_name, element_id) {
    var cur_form = document.forms[form_name];
    if (typeof(cur_form)=="undefined") { alert("The form "+form_name+" could not be found in the document."); return;}
    var slave_field = cur_form[element_id];
    if (typeof(slave_field)=="undefined") { alert("Select box "+element_id+" could not be found in the form "+form_name); return;}
    return slave_field;
}

function modifyList(list_text, cur_sel) {
    var cur_elem = getInputElementToModify(cur_sel["form"], cur_sel["slave"]);
    var options_array = list_text.split('|');
    var options_length = options_array.length;
    options_array[0] = options_array[0].replace("<div>","").replace(/^\s*<div>\s*/, "");
    options_array[options_length-1] = options_array[options_length-1].replace(/\s*<\/div>\s*$/, "");
    cur_elem.options.length = 0;
    for (var j=0; j < options_length; j++) {
        var desc_name = options_array[j].split('^');
        var newOpt = new Option(desc_name[0],desc_name[1],false,false);
        newOpt.selected = false;
        newOpt.defaultSelected = false;
        cur_elem.options[cur_elem.options.length] = newOpt;
    }
    var slave_list = _master_elements[cur_sel["form"]+'|'+cur_sel["slave"]];
    if (typeof(slave_list)!="undefined") {
        for (var i=0; i < slave_list.length; i++) {
            var slave_sel = _registry[cur_sel["form"]+'|'+cur_sel["slave"]+'|'+slave_list[i]];
            changeOnSelect(cur_elem, slave_sel["slave"], slave_sel["form"]);
        }
    }
    if (cur_elem.onchange) cur_elem.onchange();
}

function getNewOptions(selectInput, cur_key) {
    var cur_sel = _registry[cur_key];
    var url = cur_sel["url"];
    if (cur_sel["last_val"] != selectInput.value) {
        cur_sel["last_val"] = selectInput.value;
        var result = cur_sel["_cache"][selectInput.value];
        if (typeof(result)!="undefined") {
            modifyList(result,cur_sel);
            return;
        }
        var change_func = new Function("selectProcessRequestChange('"+cur_key+"','"+selectInput.value+"');")
        var selectRequest = cur_sel["_request"]
        selectRequest.onreadystatechange = change_func;
        selectRequest.open("GET", url + selectInput.value );
        selectRequest.send(null);
    }
}

function selectProcessRequestChange(cur_key, selectValue) {
    var cur_sel = _registry[cur_key];
    var selectRequest = cur_sel["_request"];
    if (selectRequest.readyState==4) {
        if (selectRequest.status==200) {
            if (typeof(cur_sel)!="undefined") {
                modifyList(selectRequest.responseText, cur_sel);
                cur_sel["_cache"][selectValue] = selectRequest.responseText;
            }
        } else {
            alert("Problem retrieving XML data from url "+cur_sel["url"]+selectValue)
        }
    }
}

function changeOnSelect(master_element, element_id, form_name) {
    var selectInput = master_element;
    var form_name = master_element.form.name;
    var cur_elem = getInputElementToModify(form_name, element_id);
    if (typeof(cur_elem)!="undefined") {
        var cur_key = form_name+'|'+selectInput.id+'|'+element_id;
        var cur_sel = _registry[cur_key];
        if (cur_sel["action"] == "vocabulary") {
            //Change slave vocabulary
            getNewOptions(selectInput, cur_key);
        } else {
            var should_hide = inArray(cur_sel["values"], selectInput.value)
            //We have a hiding value disable or hide
            if (cur_sel["action"] == "disable") {
                if (should_hide) cur_elem.disabled = true;
                else cur_elem.disabled = false;
            } else if (cur_sel["action"] == "hide") {
                //We want to hide the whole field not just the widget
                cur_elem = document.getElementById('archetypes-fieldname-'+element_id);
                if (should_hide) cur_elem.style.visibility="hidden";
                else cur_elem.style.visibility="visible";
            }
        }
    }
}

function inArray(list, value) {
    for (var i=0; i < list.length; i++) {
        if (list[i] == value) return true;
    }
    return false;
}

function registerDynamicSelect(form_name, master_id, slave_id, vocab_method, param, base_url) {
    if (base_url) var url = base_url+'/getXMLSelectVocab?method='+vocab_method+'&param='+param+'&value=';
    else var url = 'getXMLSelectVocab?method='+vocab_method+'&param='+param+'&value=';
    var select_desc = new Object();
    var key = form_name+'|'+master_id+'|'+slave_id
    select_desc["form"] = form_name;
    select_desc["master"] = master_id;
    select_desc["slave"] = slave_id;
    select_desc["action"] = "vocabulary";
    select_desc["url"] = url;
    select_desc["last_val"] = "";
    select_desc["_cache"] = new Object();
    select_desc["_request"] = new XMLHttpRequest();
    _registry[key] = select_desc;
    _all_keys.push(key);
    var all_children = _master_elements[form_name+'|'+master_id];
    if (typeof(all_children)=="undefined") all_children = new Array();
    all_children.push(slave_id);
    _master_elements[form_name+'|'+master_id] = all_children;
}

function registerHideOnSelect(form_name, master_id, slave_id, hide_action, hide_values) {
    var select_desc = new Object();
    var key = form_name+'|'+master_id+'|'+slave_id
    select_desc["form"] = form_name;
    select_desc["master"] = master_id;
    select_desc["slave"] = slave_id;
    select_desc["action"] = hide_action;
    select_desc["values"] = hide_values;
    _registry[key] = select_desc;
    _all_keys.push(key);
    var all_children = _master_elements[form_name+'|'+master_id];
    if (typeof(all_children)=="undefined") all_children = new Array();
    all_children.push(slave_id);
    _master_elements[form_name+'|'+master_id] = all_children;
}

function generateHandler(master, sel) {
    changeOnSelect(master, sel["slave"], sel["form"]);
    return new Function("changeOnSelect(this,'"+sel["slave"]+"','"+sel["form"]+"');");
}

function dynamicSelectInit() {
    for (var i=0; i < _all_keys.length; i++) {
        var cur_select = _registry[_all_keys[i]];
        var master = getInputElementToModify(cur_select["form"],cur_select["master"]);
        var change_func = generateHandler(master, cur_select);
        if (master.addEventListener) {
            master.addEventListener('change', change_func, false);
        } else if (master.attachEvent) {
            master.attachEvent('onchange', change_func);
        }
    }
}

if (window.addEventListener) window.addEventListener("load",dynamicSelectInit,false);
else if (window.attachEvent) window.attachEvent("onload", dynamicSelectInit);