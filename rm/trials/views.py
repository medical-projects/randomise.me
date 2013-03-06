"""
A create trial view?
"""
import datetime

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import DetailView, TemplateView, View, ListView
from django.views.generic.edit import CreateView

from rm import exceptions
from rm.trials.forms import TrialForm, UserTrialForm, UserReportForm
from rm.trials.models import Trial, SingleUserTrial, SingleUserReport

class LoginRequiredMixin(object):
    """
    View mixin which verifies that the user has authenticated.

    NOTE:
        This should be the left-most mixin of a view.
    """

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(*args, **kwargs)

# Views for user tabs

class MyTrials(TemplateView):
    """
    Trials associated with this user
    """
    template_name = 'trials/my_trials.html'

# Views for trials on RM users.

class TrialDetail(DetailView):
    """
    A trial detail page - this will be the unique URL for
    a trial.
    """
    context_object_name = "trial"
    model               = Trial


class TrialCreate(CreateView):
    """
    Create Me a trial please
    """
    context_object_name = "trial"
    model               = Trial
    form_class          = TrialForm

    def form_valid(self, form):
        """
        Add ownership details to the trial
        """
        form.instance.owner = self.request.user
        return super(TrialCreate, self).form_valid(form)


class JoinTrial(LoginRequiredMixin, TemplateView):
    """
    Allow a user to join a trial
    """
    template_name = 'trials/join_trial.html'

    def __init__(self, *args, **kwargs):
        """
        Add an errors container
        """
        self.errors = []
        super(JoinTrial, self).__init__(*args, **kwargs)

    def get(self, *args, **kwargs):
        """
        We visit the trial page, assign groups and
        send emails, then display a nice message.
        """
        trial = Trial.objects.get(pk=kwargs['pk'])
        self.trial = trial
        user = self.request.user
        try:
            trial.join(user)
        except exceptions.TooManyParticipantsError:
            self.errors.append('Too many participants on this trial already')
        except exceptions.AlreadyJoinedError:
            self.errors.append('You were already participating in this trial!')
        except exceptions.TrialOwnerError:
            self.errors.append('This is your trial - joining it would be wonky!')
        except exceptions.TrialFinishedError:
            self.errors.append('This trial has already finished!')
        return super(JoinTrial, self).get(self, * args, **kwargs)

    def get_context_data(self, **kw):
        """
        We'd like access to the trial in our joined template
        """
        context = super(JoinTrial, self).get_context_data(**kw)
        context['errors'] = self.errors
        context['trial']  = self.trial
        return context

# Views for trials users run on themselves
class UserTrialCreate(CreateView):
    """
    Let's make a trial!
    """
    context_object_name = 'trial'
    model               = SingleUserTrial
    form_class          = UserTrialForm

    def form_valid(self, form):
        """
        Add ownership details to the trial
        """
        form.instance.owner = self.request.user
        return super(UserTrialCreate, self).form_valid(form)


class UserReport(CreateView):
    """
    Report a single data point for this trial
    """
    context_object_name = 'report'
    model               = SingleUserReport
    form_class          = UserReportForm

    def get(self, *args,**kw):
        """
        Store the trial isntance
        """
        self.trial = SingleUserTrial.objects.get(pk=kw['pk'])
        return super(UserReport, self).get(*args, **kw)

    def post(self, *args,**kw):
        """
        Store the trial isntance
        """
        self.trial = SingleUserTrial.objects.get(pk=kw['pk'])
        return super(UserReport, self).post(*args, **kw)

    def get_context_data(self, **kw):
        """
        We want access to the trial data in the template please!
        """
        trial = getattr(self, 'trial', None)
        if not trial:
            raise ValueError()
        context = super(UserReport, self).get_context_data(**kw)
        context['trial'] = trial
        return context

    def form_valid(self, form):
        """
        We need to update the report object to set the trial
        and figure out the group that the user was allocated
        to on the date in question.
        """
        trial = getattr(self, 'trial', None)
        if not trial:
            raise ValueError()
        form.instance.trial = trial
        return super(UserReport, self).form_valid(form)


class UserTrialDetail(DetailView):
    """
    View the details of a single user trial
    """
    context_object_name = 'trial'
    model               = SingleUserTrial

# Views for trial discovery - lists, featured, etc.

class AllTrials(TemplateView):
    """
    The all trials tab of the site
    """
    template_name = 'trials.html'

    def get_context_data(self, **kw):
        """
        Add popular and featured trials to the all trials page
        """
        context = super(AllTrials, self).get_context_data(**kw)
        today = datetime.datetime.today()
        context['active'] = Trial.objects.filter(finish_date__gte=today,
                                                 private=False)
        context['active_featured'] = Trial.objects.filter(finish_date__gte=today,
                                                          featured=True,
                                                          private=False)
        context['past'] = Trial.objects.filter(finish_date__lt=today,
                                               private=False)
        return context


class FeaturedTrialsList(ListView):
    """
    This is the list view for featured Trials - an editorially
    decided subset of all trials.
    """
    queryset            = Trial.objects.filter(featured=True, private=False)
    context_object_name = 'trials'
    template_name       = 'trials/featured_trial_list.html'
