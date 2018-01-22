$(document).on('change', '#template-choice', function(){

    if($(this).val() == 'xml' || $(this).val() == 'json'){
        $("#import-select-container").removeClass('hidden')
    }else{
        $("#import-select-container").addClass('hidden')
    }

})



$(document).on('click', "#go-add-template", function(e){

    e.preventDefault()

    if($('#template-choice').val() == 'xml' || $('#template-choice').val() == 'json'){
        loadTemplate();
    }else{
        goNewTemplate();
    }
});


var loadTemplate = function(){
   
    var success = function(resp){
        //resp is the new template's ID
        var new_template = JSON.parse(resp)
        window.location.href = go_template_url + new_template['template_id']
    }

    var error = function(xhr, ajaxOptions, thrownError){
        show_error("#new-template", "An error has occurred:"  +xhr.responseJSON.message)
    }

    var form_data = new FormData($('#import_form')[0]);

    $.ajax({
        type: 'POST',
        url: load_template_url,
        data: form_data,
        contentType: false,
        processData: false,
        success: success,
        error: error
    })
}

var goNewTemplate = function(){

    window.location.href = go_new_template_url; 

}

$(document).on('click', '.delete-btn', function(){

    var net_btn = $(this).closest('li')
    var template_name = $('div.head', net_btn).text().trim()
    var template_id = net_btn.attr('id').split('_')[1]
    $('#delete-template-id-input').attr('value', template_id)
    $('#delete-template-name').attr('value', template_name)

    var tmpl_modal = $('#delete_template_modal')

    var heading = $('.name', tmpl_modal).each(function(){
        $(this).text(template_name);
    })

})

$(document).on("click", "#delete-template-button", function(event){

    event.preventDefault();

    var formdata = $("#delete-template").serializeArray();
    var data = {}
    for (var i=0; i<formdata.length; i++){
        var d = formdata[i]
        data[d['name']] = d['value']
    }

    var success = function(resp){
        $("#delete_template_modal").modal('hide')
        $("#template_"+data['template_id']).remove()
        show_success("#templatelist",  "template"+data['template_name']+" Removed")
    }

    var error = function(xhr, ajaxOptions, thrownError){
        show_error("#delete-template", "An error has occurred:"  +xhr.responseJSON.message)
    }


    $.ajax({
        url: delete_template_url,
        data : JSON.stringify(data),
        success: success,
        error: error,
        method:'POST',
    })

})

$(document).on('click', '.download-btn', function(){

    var tmpl_btn = $(this).closest('li')
    var template_name = $('div.head', tmpl_btn).text().trim()
    var template_id = tmpl_btn.attr('id').split('-')[1]
    $('#download-template-id-input').attr('value', template_id)

    var tmpl_modal = $('#download_template_modal')

    var heading = $('.name', tmpl_modal).each(function(){
        $(this).text(template_name);
    })

})

$(document).on("click", "#download-template-button", function(event){

    event.preventDefault();

    var download_url = download_template_url
    var template_id = $("#download-template-id-input").val() 
    var format     = $("#download-format").val()
    download_url = download_url + template_id + '/' + format

    window.open(download_url, '_blank')

})

