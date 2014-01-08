class @D3Chart
  constructor: (element, @options = {}) ->
    @element = $(element)
    @width = @options.width || 600
    @height = @options.height || 600
    @margin = @options.margin || {top: 50, left: 50, right: 50, bottom: 50}
  svg: ->
    @svgSelection ||= d3.select(@element[0]).append('svg')
      .attr('width', @width)
      .attr('height', @height)

  mainGroup: ->
    @mainGroupSelection ||= @svg()
      .append('g')
      .attr('class', 'main')
      .attr('transform', "translate(#{@margin.left}, #{@margin.top})")
  minMax: (data,key) ->
    max = d3.max(data, (d) -> return d[key])
    min = d3.min(data, (d) -> return d[key])
    [min, max]

  graphWidth: ->
    @width - @margin.left - @margin.right
  graphHeight: ->
    @height - @margin.top - @margin.bottom
  graphGroup: ->
    @graphGroupSelection ||= @mainGroup().append('g')
      .attr('class', 'graph')
      .attr('transform', "translate(0, 0)")
  
