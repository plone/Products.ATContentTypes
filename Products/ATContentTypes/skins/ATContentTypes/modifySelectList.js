var selectRequest = false;
var slave_list = null;
var cur_form = null;
var cur_key = "";
var selectInput = null;
var slave_list = null;
var selectLast = "";

var _registry = new Object();
var _all_keys = new Array();

function getInputElementToModify(form_name, element_id) {
    var cur_form = document.forms[form_name];
    if (typeof(cur_form)=="undefined") { alert("The form "+form_name+" could not be found in the document."); return;}
    slave_list = cur_form[element_id];
    if (typeof(slave_list)=="undefined") { alert("Select box "+element_id+" could not be found in the form "+form_name); return;}
    return slave_list;
}

function modifyList(list_text) {
    var options_array = list_text.split('|');
    var options_length = options_array.length;
    options_array[0] = options_array[0].replace("<div>","").replace(/^\s*<div>\s*/, "");
    options_array[options_length-1] = options_array[options_length-1].replace(/\s*<\/div>\s*$/, "");
    slave_list.options.length = 0;
    for (var j=0; j < options_length; j++) {
        var desc_name = options_array[j].split('^');
        var newOpt = new Option(desc_name[0],desc_name[1],false,false);
        newOpt.selected = false;
        newOpt.defaultSelected = false;
        slave_list.options[slave_list.options.length] = newOpt;
    }
}

function getNewOptions(url) {
    if (selectLast != selectInput.value) {
        var result = _registry[cur_key]["_cache"][selectInput.value];
        if (result) {
            modifyList(result);
            return;
        }
    selectRequest = Sarissa.getXmlHttpRequest();
    selectRequest.onreadystatechange= selectProcessRequestChange;
    selectRequest.open("GET", url + selectInput.value );
    _registry[cur_key]["last_val"] = selectInput.value;
    selectRequest.send(null);
    }
}

function selectProcessRequestChange() {
    modifyList(selectRequest.responseText);
    _registry[cur_key]["_cache"][selectLast] = selectRequest.responseText;
}

function changedSelection(master_element, url, element_id, form_name) {
    selectInput = master_element;
    if (typeof(form_name)!="undefined") form_name = master_element.form.name;
    getInputElementToModify(form_name, element_id);
    cur_key = form_name+selectInput.id
    if (typeof(slave_list)!="undefined") {
        getNewOptions(url);
    }
}

function registerDynamicSelect(form_name, master_id, slave_id, url) {
    var select_desc = new Object();
    select_desc["form"] = form_name;
    select_desc["master"] = master_id;
    select_desc["slave"] = slave_id;
    select_desc["url"] = url;
    select_desc["last_val"] = "";
    select_desc["_cache"] = new Object();
    _registry[form_name+master_id] = select_desc;
    _all_keys.push(form_name+master_id)
}

function dynamicSelectInit() {
    for (var i=0; i < _all_keys.length; i++) {
        var cur_select = _registry[_all_keys[i]];
        var master = getInputElementToModify(cur_select["form"],cur_select["master"]);
        if (master.onchange==null) {
            master.onchange = new Function("changedSelection(this,"+cur_select["url"]+","+cur_select["slave"]+","+cur_select["form"]+")");
        }
        changedSelection(master, cur_select["url"],cur_select["slave"],cur_select["form"]);
    }
}