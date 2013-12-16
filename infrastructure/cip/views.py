import datetime
from django.shortcuts import render_to_response, render
from infrastructure.cip.models import *
from django import forms
from django_select2 import *
from django.core.urlresolvers import *
from django.views.generic import ListView, DetailView, TemplateView
import json
import django.http
from django.contrib.humanize.templatetags.humanize import intword
from infrastructure.cip.templatetags.infrastructure_project_tags import intword_span

def index(request):
    """docstring for projects"""
    projects = Project.objects.all()
    department_needs = DepartmentNeed.objects.all()
    return render_to_response('index.haml', {'projects': projects, 'department_needs': department_needs})

def projects():
    """docstring for projects"""

def filter_projects(request):
    """docstring for filter_projects"""
    if request.POST:
        form = ProjectFilterForm(request.POST)
        form.is_valid()
        projects = ProjectFilter(form).filter()
    else:
        form = ProjectFilterForm()
    return render(request, 'projects.haml', {'projects': projects, 'form': form})

def show_project(request, p_id):
    """docstring for show_project"""
    project = Project.objects.get(id= p_id)

    return render_to_response('project.haml', {'project': project})


class ProjectStat(object):
    projects = []
    def __init__(self,projects):
        """docstring for __init__"""
        self.projects = projects
    def project_count(self):
        """docstring for project_count"""
        return self.projects.count()
    def project_cost(self):
        """docstring for project_cost"""
        return self.projects.overall_cost()

class DistrictStat(ProjectStat):
    number = 0
    councilmember = ''

    def __init__(self,district_nr,projects):
        """docstring for __init__"""
        self.number = district_nr
        self.projects = projects
    def __dict__(self):
        """docstring for __dict__"""
        return {'number': self.number,'project_count':self.project_count(), 'project_costs': self.project_cost(), 'project_cost_money_string': intword(self.project_cost()) }

class PhaseStat(ProjectStat):
    title = ''
    image_class = ''
    def __init__(self,title,projects):
        """docstring for __init__"""
        self.title = title
        self.projects = projects
    def __dict__(self):
        """docstring for __dict__"""
        return {'title': self.title,'project_count':self.project_count(), 'project_costs': self.project_cost(), 'project_cost_money_string': intword(self.project_cost()) }


class SubPhaseStat(ProjectStat):
    title = ''
    phase = ''

class Widget():
    headline = ''
    value = ''
    subtitle = ''
    widget_class = ''
    headline_link = ''
    subtitle_link = ''
    def __init__(self,headline):
        """docstring for __init__"""
        self.headline = headline
    def set_value(self,value):
        """docstring for set_value"""
        self.value = value
    def set_subtitle(self,subtitle):
        """docstring for set_value"""
        self.subtitle = subtitle

class WidgetRow():
    headline = ''
    widgets = []
    def __init__(self,headline):
       """docstring for __init"""
       self.headline = headline
       self.widgets = []

    def add_widget(self,widget):
        """docstring for add_widget"""
        self.widgets.append(widget)


class DashboardMixin(object):
    def __init__(self):
        """docstring for init"""
        self.projects = Project.objects.all()
        self.this_year = datetime.date.today().year
        self.widgets = []
    def get_widgets(self):
        """docstring for get_widgets"""
        project_widgets = ProjectWidgets()
        project_widgets.add_row('Costs',self.project_cost(),self.cost_by_year_widget(self.this_year), self.cost_by_year_widget(self.this_year+1), self.not_started_cost_widget())
        project_widgets.add_row('Projects',self.districts())
        project_widgets.add_row('Phases',self.phases())
        project_widgets.add_row('Asset Types',self.asset_types())
        return project_widgets.widgets
    def get_context_data(self, **kwargs):
        context = super(DashboardMixin, self).get_context_data(**kwargs)
        context['widgets'] = self.get_widgets()
        return context
class ProjectWidgetMixin(object):
    def construction_cost(self):
        """docstring for construction_cost"""
        construction_cost = Widget('construction \n $$$')
        construction_cost.value = intword_span(intword(self.projects.construction_cost()))
        return construction_cost
    def project_cost(self):
        """docstring for construction_cost"""
        project_cost = Widget('All projects')
        project_cost.headline_link = reverse('projects')
        project_cost.value = intword_span(intword(self.projects.overall_cost()))
        project_cost.subtitle = "{0} projects".format(self.projects.count())
        project_cost.subtitle_link = reverse('projects')
        return project_cost
    def not_started_cost_widget(self):
        """docstring for construction_cost"""
        not_started_cost = Widget('planned projects')
        not_started_cost.value = intword_span(intword(self.projects.not_started_cost()))
        not_started_cost.subtitle = "{0} projects".format(self.projects.not_started().count())
        return not_started_cost
    def cost_by_year_widget(self,year):
        """docstring for construction_cost"""
        not_started_cost = Widget('{0} projects'.format(year))
        not_started_cost.value = intword_span(intword(self.projects.cost_by_year(year)))
        not_started_cost.subtitle = "{0} projects".format(self.projects.by_year(year).count())
        return not_started_cost
    def project_count(self):
        """docstring for project_count"""
        count = Widget('projects')
        count.value =  self.projects.count()
        return count
    def active_count(self):
        """docstring for active_count"""
        count = Widget('active projects')
        count.value =  self.projects.active().count()
        return count
    def planned_count(self):
        """docstring for project_count"""
        count = Widget('planned')
        count.value =  self.projects.not_yet_started_count()
        return count
    def projects_by_year(self,year):
        """docstring for projects_by_year"""
        widget = Widget('started {0}'.format(year))
        widget.value = self.projects.count_by_year(year)
        return widget
    def finished_by_year(self,year):
        """docstring for finished_by_year"""
        widget = Widget('finished {0}'.format(year))
        widget.value = self.projects.finished_by_year(year)
        return widget

    def districts(self):
        """docstring for districts"""
        row_widgets = []
        for district in range(1,10):
            district_widget = Widget('District {0}'.format(district))
            district_widget.headline_link = reverse('district_projects',kwargs={'district': district})
            district_widget.subtitle = '{0} projects'.format(self.projects.by_district(district).count())
            district_widget.value = intword_span(intword(self.projects.by_district(district).overall_cost()))
            district_widget.widget_class = 'district-{0}'.format(district)
            row_widgets.append(district_widget)
        return row_widgets
    def phases(self):
        """docstring for phases"""
        row_widgets = []
        for (phase_class,phase) in PHASE_URLS:
            phase_widget = Widget(phase)
            phase_widget.headline_link = reverse('phase_projects',kwargs={'phase':phase_class})
            phase_widget.subtitle = '{0} projects'.format(self.projects.by_phase(phase).count())
            phase_widget.value = intword_span(intword(self.projects.by_phase(phase).overall_cost()))
            phase_widget.widget_class = phase_class
            row_widgets.append(phase_widget)
        return row_widgets
    def asset_types(self):
        """docstring for asset_types"""
        row_widgets = []
        for (asset_type_class,asset_type) in ASSET_TYPE_URLS:
            asset_widget = Widget(asset_type)
            asset_widget.headline_link = reverse('asset_type_projects',kwargs={'asset_type':asset_type_class})
            asset_widget.subtitle = '{0} projects'.format(Project.objects.all().by_asset_group(asset_type).count())
            asset_widget.widget_class = asset_type_class
            asset_widget.value = intword_span(intword(self.projects.by_asset_group(asset_type).overall_cost()))
            row_widgets.append(asset_widget)
        return row_widgets
    def project_widgets(self,filter_set):
        """docstring for project_widgets"""
        project_widgets = ProjectWidgets()
        project_widgets.add_row('Costs',self.project_cost(),self.cost_by_year_widget(datetime.date.today().year), self.not_started_cost_widget())
        #project_widgets.add_row('',self.project_count(),self.project_cost(),self.construction_cost())
        if not filter_set.has_key('district'):
            project_widgets.add_row('Projects',self.districts())
        if not filter_set.has_key('phase'):
            project_widgets.add_row('Phases',self.phases())
        if not filter_set.has_key('asset_type'):
            project_widgets.add_row('Asset Types',self.asset_types())
        project_widgets.add_row('',self.projects_by_year(datetime.date.today().year))
        return project_widgets.widgets

class ProjectsFilterMixin():
    projects = Project.objects.all()

    def filter(self,filter_by,value):
        """docstring for filter"""
        getattr(self, filter_by)(value)
        return self.projects
    def filter_by_phase(self,value):
        """docstring for phase"""
        self.projects = self.projects.order_by(PHASE_ORDERS[value]).by_phase(dict(PHASE_URLS)[value])
    def filter_by_asset_type(self,value):
        """docstring for asset_type"""
        self.projects = self.projects.by_asset_group(dict(ASSET_TYPE_URLS)[value]).order_by('SP_CONSTR_FINISH_DT')
    def filter_by_district(self,value):
        """docstring for district"""
        self.projects = self.projects.by_district(value).order_by('SP_CONSTR_FINISH_DT')

class DashboardView(DashboardMixin, ProjectWidgetMixin, TemplateView):
    template_name = 'dashboard.haml'


class ProjectDetailView(DetailView):
    model = Project
    template_name = 'project.haml'
    context_object_name = 'project'
    slug_field = 'SP_SAPNO'
class ProjectList(ListView,ProjectsFilterMixin,ProjectWidgetMixin):
    model = Project
    context_object_name = 'projects'
    template_name = 'projects.haml'
    paginate_by = 20
    form_data = {'dataset': 'all', 'order': 'SP_PRELIM_ENGR_START_DT'}

    def timephase(self):
        """docstring for timephase"""
        self.show = {'current': 'active', 'all': ''}
        projects = Project.objects.all()
        if self.kwargs.has_key('show'):
            if self.kwargs['show'] == "current":
                self.show['current'] = 'active'
                self.show['all'] = ''
                projects = Project.objects.current()
            elif self.kwargs['show'] == 'all':
                self.show['current'] = ''
                self.show['all'] = 'active'
                projects = Project.objects.all()
        return projects.order_by('SP_PRELIM_ENGR_START_DT').exclude(SP_PRELIM_ENGR_START_DT=None)
    def reset_form_data(self):
        """docstring for reset_form_data"""
        self.form_data = {'dataset': 'all', 'order': 'SP_PRELIM_ENGR_START_DT'}
    def get_queryset(self):
        """docstring for get_queryset"""
        projects = []
        self.show = {'current': '', 'all': 'active'}
        if self.kwargs.has_key('phase'):
            self.reset_form_data()
            self.filter('filter_by_phase',self.kwargs['phase'])
            for key, value in dict(PROJECT_PHASES).items():
                if value == dict(PHASE_URLS)[self.kwargs['phase']]:
                    self.form_data['current_phase'] = key
        if self.kwargs.has_key('asset_type'):
            self.reset_form_data()
            self.filter('filter_by_asset_type',self.kwargs['asset_type'])
            for key, value in dict(ASSET_TYPE_GROUPS).items():
                if value == dict(ASSET_TYPE_URLS)[self.kwargs['asset_type']]:
                    self.form_data['asset_type'] = key
        if self.kwargs.has_key('district'):
            self.reset_form_data()
            self.filter('filter_by_district',self.kwargs['district'])
            self.form_data['district'] = self.kwargs['district']

        return self.projects

    def get_context_data(self, **kwargs):
        """docstring for get_contxt_data"""
        context = super(ProjectList, self).get_context_data(**kwargs)
        context['form'] = ProjectFilterForm(self.form_data)
        context['widgets'] = self.project_widgets({})
        context['show'] = self.show
        return context

class ProjectsListListView(ProjectList):
    template_name = 'project_list.haml'
    paginate_by = 10

    def get(self, request, *args, **kwargs):
        form = ProjectFilterForm(self.request.GET)
        if form.is_valid():
            pf = ProjectFilter(form)
            self.projects =  pf.filter()
        kwargs['object_list'] = self.projects
        context = super(ProjectList, self).get_context_data(**kwargs)
        if form.is_valid():
            context['filter'] = pf.filter_set
            context['widgets'] = self.project_widgets(pf.filter_set)
        return render(request, self.template_name, context)

class ProjectStatsView(TemplateView):
    template_name="stats.haml"
    def get_projects(self):
        """docstring for get_projects"""
        return Project.objects.all()
    def get_stats(self):
        """docstring for get_stats"""
        stats = {}
        stats["project_count"] = self.projects.count()
        stats["project_cost"] = self.projects.overall_cost()
        stats["phases"] = []
        for (phase_class,phase) in PHASE_URLS:
            phase_stat = PhaseStat(phase,self.projects.by_phase(phase))
            stats["phases"].append({phase: phase_stat.__dict__() })
        stats["asset_types"] = []
        for (asset_type_class,asset_type) in ASSET_TYPE_URLS:
            stats["asset_types"].append({asset_type: self.projects.by_asset_group(asset_type).count()})
        stats["specific_asset_types"] = []
        for (key,value) in ASSET_TYPE_CHOICES:
            stats["specific_asset_types"].append({value: self.projects.by_asset_choice(key).count()})
        stats["districts"] = {}
        for district_nr in range(1,10):
            district = DistrictStat(district_nr,self.projects.by_district(district_nr))
            stats["districts"][district_nr] = district.__dict__()
        return stats

    def get_context_data(self, **kwargs):
        context = super(ProjectStatsView, self).get_context_data(**kwargs)
        self.projects = self.get_projects()
        context["stats"] = self.get_stats()
        return context
class ProjectStatsJSONMixin(object):
    def render_to_response(self, context):
        "Returns a JSON response containing 'context' as payload"
        return self.get_json_response(self.convert_context_to_json(context))

    def get_json_response(self, content, **httpresponse_kwargs):
        "Construct an `HttpResponse` object."
        return django.http.HttpResponse(content,
                                 content_type='application/json',
                                 **httpresponse_kwargs)

    def convert_context_to_json(self, context):
        stats = context["stats"]
        return json.dumps(stats)

class ProjectStatsJSONView(ProjectStatsJSONMixin,ProjectStatsView):
    pass

class ProjectWidgets(object):
    def __init__(self):
        self.widgets = []
    def add_row(self,title,*widgets):
        """docstring for add_row"""
        row = WidgetRow(title)
        row_widgets = []
        for widget in list(widgets):
            if isinstance(widget, Widget):
                row_widgets.append(widget)
            else:
                row_widgets = row_widgets + widget
        row.widgets = row_widgets
        self.widgets.append(row)

class ProjectFilter:
    def __init__(self, form):
        self.form = form
        self.projects = Project.objects.all()
        if self.form.cleaned_data['dataset'] == 'active':
            self.projects = self.projects.active()
        elif self.form.cleaned_data['dataset'].isdigit():
            self.projects = self.projects.by_year(int(self.form.cleaned_data['dataset']))
        if self.form.cleaned_data.has_key('order') and self.form.cleaned_data['order']:
            self.order =  self.form.cleaned_data['order']
            self.filter_set = { 'order': dict(ORDER)[self.order] }
        else:
            self.order = 'SP_PRELIM_ENGR_START_DT'
            self.filter_set = {'order': 'SP_PRELIM_ENGR_START_DT'}
    def filter(self):
        """docstring for  filter_data"""
        if self.form.cleaned_data.has_key('current_phase') and self.form.cleaned_data['current_phase']:
            self.phases()
        if self.form.cleaned_data.has_key('asset_type') and self.form.cleaned_data['asset_type']:
            self.asset_types()
        if self.form.cleaned_data.has_key('specific_asset_type') and self.form.cleaned_data['specific_asset_type']:
            self.asset_groups()
        if self.form.cleaned_data.has_key('delivery_method') and self.form.cleaned_data['delivery_method']:
            self.delivery_methods()
        if self.form.cleaned_data.has_key('client_department') and self.form.cleaned_data['client_department']:
            self.client_departments()
        if self.form.cleaned_data.has_key('project_cost') and self.form.cleaned_data['project_cost']:
            self.project_cost()
        if self.form.cleaned_data.has_key('district') and self.form.cleaned_data['district']:
            self.districts()
        return self.projects.order_by(self.order).exclude(**{self.order.replace('-',''): None})

    def phases(self):
        """docstring for phases"""
        phase = self.form.cleaned_data['current_phase']
        phases = dict(PROJECT_PHASES)
        self.filter_set['phase'] = phases[phase]
        self.projects = self.projects.by_phase(phases[phase])
    def asset_types(self):
        """docstring for asset_types"""
        asset_type = self.form.cleaned_data['asset_type']
        asset_types = dict(ASSET_TYPE_GROUPS)
        self.filter_set['asset_type'] = asset_types[asset_type]
        self.projects = self.projects.by_asset_group(asset_types[asset_type])
    def asset_groups(self):
        """docstring for asset_types"""
        asset_group = self.form.cleaned_data['specific_asset_type']
        asset_groups = dict(ASSET_TYPE_CHOICES)
        self.projects = self.projects.by_asset_group(asset_groups[asset_group])
    def delivery_methods(self):
        """docstring for asset_types"""
        delivery_method = self.form.cleaned_data['delivery_method']
        delivery_methods = dict(DELIVERY_METHODS)
        self.projects = self.projects.by_delivery_method(delivery_methods[delivery_method])
    def client_departments(self):
        """docstring for asset_types"""
        client_department = self.form.cleaned_data['client_department']
        client_departments = dict(CLIENT_DEPARTMENTS)
        self.projects = self.projects.by_client_department(client_departments[client_department])
    def project_cost(self):
        """docstring for project_cost"""
        project_cost = self.form.cleaned_data['project_cost']
        self.projects = self.projects.by_project_cost(ProjectCosts().get_value(int(project_cost)))
    def districts(self):
        """docstring for project_cost"""
        district = self.form.cleaned_data['district']
        self.filter_set['district'] = district
        self.projects = self.projects.by_district(district)

class ProjectFilterForm(forms.Form):
    default = [(u'', 'All')]
    year = datetime.date.today().year
    choice_phases = tuple(default + list(PROJECT_PHASES))
    choice_assets = tuple(default + list(ASSET_TYPE_GROUPS))
    choice_type_choices = tuple(default + list(ASSET_TYPE_CHOICES))
    choice_delivery_methods = tuple(default + list(DELIVERY_METHODS))
    choice_client_departments = tuple(default + list(CLIENT_DEPARTMENTS))
    project_costs = tuple(default + ProjectCosts().get_touples())
    choice_districts = tuple(default + Districts().get_touples())

    project_cost = Select2ChoiceField(
        choices=project_costs, required=False)
    current_phase = Select2ChoiceField(initial=2,
        choices=choice_phases,required=False)
    asset_type = Select2ChoiceField(initial=2,
        choices=choice_assets,required=False)
    specific_asset_type = Select2ChoiceField(initial=2,
        choices=choice_type_choices,required=False)
    client_department = Select2ChoiceField(initial=2,
        choices=choice_client_departments,required=False)
    delivery_method = Select2ChoiceField(initial=2,
        choices=choice_delivery_methods,required=False)
    district = Select2ChoiceField(initial=2,
        choices=choice_districts,required=False)
    dataset = Select2ChoiceField(initial=1,
        choices=(('all','All'),('active','Active'),(year-1,year-1),(year,year),(year+1,year+1)),required=False)
    order = Select2ChoiceField(initial=1,
        choices=(ORDER),required=False)

class JSONTimetableMixin(object):
    def render_to_response(self, context):
        "Returns a JSON response containing 'context' as payload"
        return self.get_json_response(self.convert_context_to_json(context))

    def get_json_response(self, content, **httpresponse_kwargs):
        "Construct an `HttpResponse` object."
        return django.http.HttpResponse(content,
                                 content_type='application/json',
                                 **httpresponse_kwargs)

    def convert_context_to_json(self, context):
        "Convert the context dictionary into a JSON object"
        project = context["project"]
        json_response = {
                "timeline": {
                "headline":"Project Timeline",
                "type":"default",
                "text":"<p></p>",
                "date": []
                }
            }
        if project.SP_PRELIM_ENGR_START_DT and project.SP_PRELIM_ENGR_FINISH_DT:
            json_response["timeline"]["date"].append({
                        "startDate":project.SP_PRELIM_ENGR_START_DT.strftime("%Y,%m,%d"),
                        "endDate":project.SP_PRELIM_ENGR_FINISH_DT.strftime("%Y,%m,%d"),
                        "headline":"Planning Phase",
                    })
        if project.SP_DESIGN_INITIATION_START_DT and project.SP_DESIGN_FINISH_DT:
            json_response["timeline"]["date"].append({
                        "startDate":project.SP_DESIGN_INITIATION_START_DT.strftime("%Y,%m,%d"),
                        "endDate":project.SP_DESIGN_FINISH_DT.strftime("%Y,%m,%d"),
                        "headline":"Design Phase",
                    })
        if project.SP_BID_START_DT and project.SP_BID_FINISH_DT:
            json_response["timeline"]["date"].append({
                        "startDate":project.SP_BID_START_DT.strftime("%Y,%m,%d"),
                        "endDate":project.SP_BID_FINISH_DT.strftime("%Y,%m,%d"),
                        "headline":"Bid Phase",
                    })
        if project.SP_AWARD_START_DT and project.SP_AWARD_FINISH_DT:
            json_response["timeline"]["date"].append({
                        "startDate":project.SP_AWARD_START_DT.strftime("%Y,%m,%d"),
                        "endDate":project.SP_AWARD_FINISH_DT.strftime("%Y,%m,%d"),
                        "headline":"Award Phase",
                    })
        if project.SP_CONSTRUCTION_START_DT and project.SP_CONSTR_FINISH_DT:
            json_response["timeline"]["date"].append({
                        "startDate":project.SP_CONSTRUCTION_START_DT.strftime("%Y,%m,%d"),
                        "endDate":project.SP_CONSTR_FINISH_DT.strftime("%Y,%m,%d"),
                        "headline":"Construction Phase",
                    })
        if project.SP_CONSTR_FINISH_DT and project.SP_NOC_DT:
            json_response["timeline"]["date"].append({
                        "startDate":project.SP_CONSTR_FINISH_DT.strftime("%Y,%m,%d"),
                        "endDate":project.SP_NOC_DT.strftime("%Y,%m,%d"),
                        "headline":"Post-Construction Phase",
                    })
        return json.dumps(json_response)
class ProjectDetailJSONView(JSONTimetableMixin, ProjectDetailView):
    pass

class DistrictView(TemplateView):
    template_name = 'districts.haml'
