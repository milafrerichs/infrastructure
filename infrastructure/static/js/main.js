$(document).ready(function() {
  $('#nav').on('click','#search', function() {
    value = $(this).val()
    if(value == "Search...") {
      $(this).val('');
    }
  }).on('blur', '#search', function() {
    value = $(this).val()
    if(value == '') {
      $(this).val('Search...');
    }
  });
  $( "form#projects-filter" ).on( "submit", function( event ) {
    event.preventDefault();
    form_data = $(this).serialize();
    $.ajax({
      url: '/projects_list',
      data: form_data,
    }).done(function(data) { 
      $('#project-list').html(data);
    });
  });
  $(document).on("click", ".remote #pagination a", function(event) {
    event.preventDefault();
    $('form #page').val($(this).data('page'));
    $('form').submit();
  });
  $('#projects_filter').on('click', '#submit', function(event) {
    $('form #page').val('1');
  });
  if($('#project').length > 0) {
    project_width =  $('#project').width();
    project_id = $('#project').data('id');
    first_column_width = $('#project #map').width();
    createStoryJS({
        type:       'timeline',
        width:      project_width,
        height:     '340',
        source:     '/project/'+ project_id +'/timetable.json',
        embed_id:   'timeline'           // ID of the DIV you want to load the timeline into
    });
    var map = L.mapbox.map('map', 'milafrerichs.map-ezn7qjpd')
    .setView([32.70752, -117.15706], 9);

    cost_data = $('#project-cost').data('cost').split(',');
    cost_data = cost_data.map(function(d) { return parseInt(d); });
    cost_labels = $('#project-cost').data('cost-labels').split(',');
    cost_x_scale = d3.scale.ordinal().rangeRoundBands([0, first_column_width-20], .1).domain(cost_data);
    cost_x_axis_scale = d3.scale.ordinal().rangeRoundBands([0, first_column_width-20], .1).domain(cost_labels);
    cost_y_scale = d3.scale.linear().range([100,0]).domain([0, d3.max(cost_data)]);
    var svg_element = d3.select('#cost-breakdown').append('svg').attr('height','160').attr('width',first_column_width).append('g').attr('transform','translate(20,20)');
    svg_element.selectAll('rect').data(cost_data).enter().append('rect').attr('x',function(d) { return cost_x_scale(d); }).attr("width", cost_x_scale.rangeBand()).attr('y', function(d) {return cost_y_scale(d)}).attr('height',function(d) {return 120-cost_y_scale(d);});
    x_axis = d3.svg.axis().scale(cost_x_axis_scale).orient('bottom');
    svg_element.append('g').attr('class','axis x').attr("transform", "translate(0,120)").call(x_axis);
  }

  if($('#main').length > 0) {
    L.esri.get = L.esri.RequestHandlers.JSONP;
    var map = L.mapbox.map('map', 'milafrerichs.map-ezn7qjpd')
    .setView([32.70752, -117.15706], 11);
    districtLayer = L.esri.dynamicMapLayer('http://maps.sandiego.gov/ArcGIS/rest/services/CIPTrackingPublic/MapServer',{
      'layers': [15],
      'opacity' :0.9
    }).addTo(map);
    dynLayer = L.esri.dynamicMapLayer('http://maps.sandiego.gov/ArcGIS/rest/services/CIPTrackingPublic/MapServer',{
      'layers': [1,2,3,4],
      'opacity' :1
    }).addTo(map);
    map.on("click", function(e) {
        districtLayer.identify(e.latlng, function(data) {
          if(data.results.length > 0) {
            console.log(data.results);
            cipLayer = data.results[0];
            if(cipLayer.layerName == "CIP Point" || cipLayer.layerName == "CIP Line" || cipLayer.layerName == "CIP Poly"  ) {
              attributes = cipLayer.attributes;
              projectId = attributes["PROJECT ID"];
              projectTitle = attributes["TITLE"];
              projectUrl = '/project/' + projectId;
              popupText = '<h4>' + projectTitle + '</h4><a href="' + projectUrl + '">Detail</a>'
              var popup = L.popup()
              .setLatLng(e.latlng)
              .setContent(popupText)
              .openOn(map);
            }
          }
        });
    });
  }
  if($('#project-list .tabs').length > 0) {
    $('#project-list').on('click', '.tabs li a',function(e) {
      $('.tab-view').hide();
      $('#' + $(this).data('tab')).show();
      $('#project-list .tabs li').removeClass('active');
      $(this).parent('li').addClass('active');
    });
  }
});
