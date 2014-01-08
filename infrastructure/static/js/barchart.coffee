class @DistrictBarChart extends D3Chart
  constructor: (element, @options = {}) ->
    super(element, @options)
  xAxisGroup: ->
    @xAxisGroupSelection ||= @graphGroup().append('g')
      .attr('class', 'axis x-axis')
      .attr('transform', "translate(0, #{@graphHeight()})")
  xAxis: ->
    xAxis = d3.svg.axis().scale(@xScale).orient('bottom').ticks(9)
    @xAxisGroup().call(xAxis)
  chart: (@data,@type) ->
    @quantize = d3.scale.quantize()
    .domain(@minMax(@data,@type))
    .range(d3.range(8).map((i) -> return "gb" + i + "-8"))
    @xScale = d3.scale.ordinal().domain(["1","2","3","4","5","6","7","8","9"]).rangeRoundBands([0, @graphWidth()], 0.05)
    @yScale = d3.scale.linear().domain([0,d3.max(@data,(d) => d[@type])]).range([@graphHeight(),0])
    graphs = @mainGroup().selectAll("rect").data(@data)
    graphs.enter()
    .append("rect")
    graphs
    .attr("width", @xScale.rangeBand())
    .attr("height", (d) => @graphHeight() - @yScale(d[@type]) )
    .attr("y", (d) => @yScale(d[@type]))
    .attr('transform', (d) => "translate(#{@xScale(d.District)}, 0)" )
    .attr("class", (d) => @quantize(d[@type]))
    graphs.exit().remove()
    @xAxis()
