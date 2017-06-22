d3.selectAll('.attr-restriction-btn').on('click', function(){
  var btn = d3.select(this)
  var td = btn.node().parentNode;
  var tr = td.parentNode;
  var attr_name = d3.select(tr).select("input[name='attr_name']").property('value');
  var data_type = d3.select(tr).select("select.data_types").property('value')
  d3.select('#restriction-modal .attr-name').text(attr_name);
  d3.select('#restriction-modal input.data_type').property('value', data_type);
  d3.select('#restriction-modal .restriction-id').property('value', btn.attr('target'))

  var curr_restriction = JSON.parse(d3.select(td).select('input').property('value'))

  for (var k in curr_restriction){
    //Clone the template row and put it into the table with the restriction values
    var restrictionrow = $('#restriction-template')
    var newrow = d3.select('#restriction-table')
                    .append('tr')
                    .classed(k, true)
                    .classed('restriction', true)
                    .html(restrictionrow.html())
    //Get the restriciton text from the dropdown, and set that element to be disabled,
    //as it's already selected.
    restriction_option = d3.select("#restriction-select option[value="+k+"]")
    restriction_option.attr('disabled', 'disabled')
    restriction_text = restriction_option.text()
    //Fill in the data.
    newrow.select('td.restriction-name').text(restriction_text);
    newrow.select('td.restriction-data input').property('value', curr_restriction[k]);

    //Attach a delete handler to the delete button in the row
    newrow.select(".restriction-delete .btn").on('click', function(){
        //Parent node = td
        //td.parentNode = tr
        d3.select(this).node().parentNode.parentNode.remove()
        selected_restriction.attr('disabled', null)
    })

  }
  $("#restriction-select").selectpicker('refresh')


})

d3.select('#add-restriction').on('click', function(){
    var selected_restriction = d3.select("#restriction-select")
            .selectAll('option')
            .filter(function(){
              return this.selected;
            })
    var new_restriction_val  = selected_restriction.attr('value')
    var new_restriction_text = selected_restriction.text()
    selected_restriction.attr('disabled', 'disabled')
    $("#restriction-select").selectpicker('refresh')

    var restrictionrow = $('#restriction-template')

    var newrow = d3.select('#restriction-table')
                    .append('tr')
                    .classed(new_restriction_val, true)
                    .classed('restriction', true)
                    .html(restrictionrow.html())

    newrow.select('td:first-child').text(new_restriction_text);

    //Attach a delete handler to the delete button in the row
    newrow.select(".restriction-delete .btn").on('click', function(){
        //Parent node = td
        //td.parentNode = tr
        d3.select(this).node().parentNode.parentNode.remove()
        selected_restriction.attr('disabled', null)
    })

})

d3.select("#save-restrictions-button").on('click', function(){
    var all_inputs_valid = true;
    var restrictions = {}
    d3.event.stopPropagation()
    d3.selectAll("#restriction-table .restriction-text").each(function(){
      var input = d3.select(this)
      var value = input.property('value')
      if (value == ''){
        input.classed('error', true)
        all_inputs_valid = false;
      }else{

        var data_type = d3.select('#restriction-modal input.data_type').property('value')
        input.classed('error', false)
        var row = input.node().parentNode.parentNode
        var restriction_type = row.classList[0];
        //A comma-sepearated list must be json serialisable.
        try{
          if (data_type == 'descriptor'){
            var value = input.property('value');
            var splitval = value.split(',');
            var strval = '[';
            splitval.forEach(function(v, i){
                strval = strval + '"'+v+'"'
                if (i != splitval.length-1){
                    strval = strval + ','
                }
            })
            strval = strval + ']';
            value = JSON.parse(strval);
          }else{
            var value = JSON.parse("[" + input.property('value') + "]");
          }
        }catch(Error){
          input.classed('error', true)
          all_inputs_valid = false;
        }
        restrictions[restriction_type] = value
      }
    })
    if (all_inputs_valid == true){
      //Set the value on the input row
      var restriction_input = d3.select('#restriction-modal .restriction-id').property('value')
      d3.select('#'+restriction_input).property('value', JSON.stringify(restrictions))
      //Reset the modal and hide it.
      $('#restriction-modal').modal('hide');

    }
})

$("#restriction-modal").on('hidden.bs.modal', function(){
  d3.selectAll('#restriction-table tr.restriction').remove()
  d3.selectAll("#restriction-select").selectAll('option').attr('disabled', null)
  $("#restriction-select").selectpicker('refresh')
})

d3.selectAll("#restriction-container .restriction-delete btn").on('click', function(){
    d3.event.stopPropagation()
    alert('deleting row')
})
