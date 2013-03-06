"""
Custom forms for the creation of Trials
"""
from form_utils.forms import BetterModelForm

from rm.trials.models import Trial, SingleUserTrial, SingleUserReport
from rm.trials.validators import not_historic

class TrialForm(BetterModelForm):
    """
    Custom user presentation of trials
    """
    class Meta:
        model = Trial
        fieldsets = [
            ('Basic', {'fields': ['name', 'url', 'private'],
                       'legend': 'Basic Details',
                       'description': ''}),
            ('Setup', {'fields': ['description', 'style'],
                       'legend': 'Trial Setup',
                       'classes': ['collapsed']}),
            ('Details', {'fields': ['group_a', 'group_b'],
                         'legend': 'Trial Details',
                         'classes': ['collapsed']}),
            ('Sizing', {'fields': ['min_participants', 'max_participants'],
                        'legend': 'Trial Sizing',
                        'classes': ['collapsed']}),
            ('Duration', {'fields': ['finish_date'],
                          'legend': 'Trial Duration',
                          'classes': ['collapsed']})
            ]

    def clean_finish_date(self):
        """
        Can we validate that the finish_date isn't in the past please?
        """
        not_historic(self.cleaned_data['finish_date'])

class UserTrialForm(BetterModelForm):
    """
    Creating a single user trial for our users
    """
    class Meta:
        model = SingleUserTrial
        fieldsets = [
            ('Basic', {'fields': ['name'],
                       'legend': 'Basic Details',
                       'description': ''}),
            ('Setup', {'fields': ['question', 'variable'],
                       'legend': 'Trial Setup',
                       'classes': ['collapsed']}),
            ('Details', {'fields': ['group_a', 'group_b'],
                         'legend': 'Trial Details',
                         'classes': ['collapsed']}),
            ('Duration', {'fields': ['start_date', 'finish_date'],
                          'legend': 'Trial Duration',
                          'classes': ['collapsed']})
            ]

    # def clean_finish_date(self):
    #     """
    #     Can we validate that the finish_date isn't in the past please?
    #     """
    #     not_historic(self.cleaned_data['finish_date'])

    # def clean_start_date(self):
    #     """
    #     Can we validate that the start_date isn't in the past please?
    #     """
    #     not_historic(self.cleaned_data['start_date'])

class UserReportForm(BetterModelForm):
    """
    Allow the reporting of data for a trial.
    """
    class Meta:
        model = SingleUserReport
        fieldsets = [
            ('Main', {'fields': ['date', 'score'],
                       'legend': 'Report Data',
                       'description': ''}),

            ]
