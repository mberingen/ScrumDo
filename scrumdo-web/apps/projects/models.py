# ScrumDo - Agile/Scrum story management web application
# Copyright (C) 2011 ScrumDo LLC
#
# This software is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy (See file COPYING) of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301  USA


from datetime import datetime, date, timedelta
import time
from tagging.fields import TagField
from tagging.models import Tag
import tagging
import re
import random
import string
from itertools import groupby

from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.db import models
from groups.base import Group
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist

from organizations.models import Organization, Team

import django.dispatch
import projects.signals as signals

STATUS_TODO = 1
STATUS_DOING = 2
STATUS_REVIEWING = 3
STATUS_DONE = 4
STATUS_CHOICES = (
    (1, "TODO"), (2, "In Progress"),  (3, "Reviewing"), (4, "Done"))
STATUS_REVERSE = {"TODO": STATUS_TODO, "Doing": STATUS_DOING, "In Progress":
                  STATUS_DOING,  "Reviewing": STATUS_REVIEWING,  "Done": STATUS_DONE}

import logging

logger = logging.getLogger(__name__)


class SiteStats(models.Model):
    user_count = models.IntegerField()
    project_count = models.IntegerField()
    story_count = models.IntegerField()
    date = models.DateField(auto_now=True)

    def __unicode__(self):
        return "%s %d/%d/%d" % (self.date, self.project_count, self.story_count, self.user_count)


class PointsLog(models.Model):
    date = models.DateField(auto_now=True)
    points_claimed = models.IntegerField()
    points_total = models.IntegerField()
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    related_object = generic.GenericForeignKey('content_type', 'object_id')

    def timestamp(self):
        return int((time.mktime(self.date.timetuple()) - time.timezone) * 1000)

    class Meta:
        ordering = ["date"]


class Project(Group):
    POINT_CHOICES_FIBO = (('?', '?'), ('0', '0'), ('0.5', '0.5'), ('1', '1'),  ('2', '2'),  ('3', '3'),  (
        '5', '5'), ('8', '8'), ('13', '13'), ('20', '20'), ('40', '40'), ('100', '100'), ('Inf', 'Infinite'))
    POINT_CHOICES_MINIMAL = (('?', '?'), ('0', '0'),  (
        '1', '1'),  ('2', '2'),  ('3', '3'),  ('4', '4'), ('5', '5'))
    POINT_CHOICES_MAX = (('?', '?'), ('0', '0'), ('0.5', '0.5'), ('1', '1'),  ('2', '2'),  ('3', '3'),   ('4', '4'), ('5', '5'),  ('6', '6'),  (
        '7', '7'), ('8', '8'),  ('9', '9'),  ('10', '10'), ('15', '15'), ('25', '25'), ('50', '50'), ('100', '100'), ('Inf', 'Infinite'))
    POINT_CHOICES_SIZES = (('?', '?'), ('1', 'XS'), (
        '5', 'S'), ('10', 'M'), ('15', 'L'),  ('25', 'XL'))
    POINT_RANGES = [POINT_CHOICES_FIBO, POINT_CHOICES_MINIMAL,
                    POINT_CHOICES_MAX, POINT_CHOICES_SIZES]

    VELOCITY_TYPE_AVERAGE = 0
    VELOCITY_TYPE_AVERAGE_5 = 1
    VELOCITY_TYPE_MEDIAN = 2
    VELOCITY_TYPE_AVERAGE_3 = 3

    active = models.BooleanField(default=True)
    member_users = models.ManyToManyField(
        User, through="ProjectMember", related_name="user_projects", verbose_name=_('member_users'))
    # private means only members can see the project
    private = models.BooleanField(_('private'), default=True)
    points_log = generic.GenericRelation(PointsLog)
    current_iterations = None
    default_iteration = None
    use_assignee = models.BooleanField(default=False)
    use_tasks = models.BooleanField(default=False)
    use_extra_1 = models.BooleanField(default=False)
    use_extra_2 = models.BooleanField(default=False)
    use_extra_3 = models.BooleanField(default=False)
    extra_1_label = models.CharField(max_length=25, blank=True, null=True)
    extra_2_label = models.CharField(max_length=25, blank=True, null=True)
    extra_3_label = models.CharField(max_length=25, blank=True, null=True)
    velocity_type = models.PositiveIntegerField(default=1)
    point_scale_type = models.PositiveIntegerField(default=0)
    velocity = models.PositiveIntegerField(null=True)
    velocity_iteration_span = models.PositiveIntegerField(null=True)
    iterations_left = models.PositiveIntegerField(null=True)
    organization = models.ForeignKey(
        Organization, related_name="projects", null=True, blank=True)
    category = models.CharField(
        max_length=25, blank=True, null=True, default="")
    categories = models.CharField(max_length=1024, blank=True, null=True)
    token = models.CharField(max_length=7, default=lambda: "".join(
        random.sample(string.lowercase + string.digits, 7)))

    class Meta:
        ordering = ['-active', 'name']

    def getCategoryList(self):
        if self.categories:
            return [c.strip() for c in self.categories.split(",")]
        else:
            return []

    def getPointScale(self):
        return self.POINT_RANGES[self.point_scale_type]

    def getNextEpicId(self):
        if self.epics.count() == 0:
            return 1
        return self.epics.order_by('-local_id')[0].local_id + 1

    def getNextId(self):
        if self.stories.count() == 0:
            return 1
        return self.stories.order_by('-local_id')[0].local_id + 1

    def all_member_choices(self):
        members = self.all_members()
        choices = []
        for member in members:
            choices.append([member.id, member.username])
        choices = sorted(choices, key=lambda user: user[1].lower())
        return choices

    def all_members(self):
        members = []
        for membership in self.members.all():
            members.append(membership.user)

        for team in self.teams.all():
            for member in team.members.all():
                if not member in members:
                    members.append(member)
        return members

    def get_member_by_username(self, username):
        members = self.all_members()
        for member in members:
            if member.username == username:
                return member
        return None

    def hasReadAccess(self, user):
        if self.creator == user:
            return True
        return Organization.objects.filter(teams__members__user=user, teams__access_type="read", teams__projects__project=self).count() > 0

    def hasWriteAccess(self, user):
        if self.creator == user:
            return True
        return Organization.objects.filter(teams__members__user=user, teams__access_type__ne="read", teams__projects__project=self).count() > 0

    def get_default_iteration(self):
        if self.default_iteration is None:
            iterations = Iteration.objects.filter(
                project=self, default_iteration=True)
            if len(iterations) == 0:
                # Shouldn't really happen, but just in case.
                self.default_iteration = self.iterations.all()[0]
            else:
                self.default_iteration = iterations[0]
        return self.default_iteration

    def get_current_iterations(self):
        if self.current_iterations is None:
            today = date.today
            self.current_iterations = self.iterations.filter(
                start_date__lte=today, end_date__gte=today)
        return self.current_iterations

    def get_absolute_url(self):
        return reverse('project_detail', kwargs={'group_slug': self.slug})

    def member_queryset(self):
        return self.member_users.all()

    def user_is_member(self, user):
        # @@@ is there a better way?
        if ProjectMember.objects.filter(project=self, user=user).count() > 0:
            return True
        else:
            return False

    def get_num_stories(self):
        return Story.objects.filter(project=self).count()

    def get_num_iterations(self):
        return Iteration.objects.filter(project=self).count()

    def get_url_kwargs(self):
        return {'group_slug': self.slug}

    def unique_tags(self):
        all_tags = self.tags.all().order_by("name")
        tags = []
        for tag in all_tags:
            #remove duplicates
            if len([t for t in tags if t.name == tag.name]) == 0:
                tags.append(tag)
        return tags

    def get_iterations(self):
        if self.get_num_iterations <= 15:
            return self.iterations.all()
        else:
            return self.iterations.filter(models.Q(default_iteration=True) |  # We always show the backlog.
                                          # And we show iterations without
                                          # dates on either end
                                          models.Q(start_date=None) | models.Q(end_date=None) |
                                          # We show past iterations within 30
                                          # days
                                          models.Q(end_date__gt=datetime.today() - timedelta(days=30), end_date__lte=datetime.today()) |
                                          # and future iterations within 30
                                          # days
                                          models.Q(start_date__gte=datetime.today(), start_date__lt=datetime.today() + timedelta(days=30)) |
                                          # And current iterations too
                                          models.Q(
                                              start_date__lte=datetime.today(), end_date__gte=datetime.today())
                                          )

    def get_iterations_all(self):
        return self.iterations.all()

    def show_more(self):
        return self.get_num_iterations() > 15


class Iteration(models.Model):
    name = models.CharField("name", max_length=100)
    detail = models.TextField(_('detail'), blank=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    project = models.ForeignKey(Project, related_name="iterations")
    default_iteration = models.BooleanField(default=False)
    points_log = generic.GenericRelation(PointsLog)
    locked = models.BooleanField(default=False)

    include_in_velocity = models.BooleanField(
        _('include_in_velocity'), default=True)

    def isCurrent(self):
        today = date.today()
        return self.start_date <= today and self.end_date >= today

    def total_points(self):
        return sum(map(lambda story: story.points_value(), self.stories.all()))

    def completed_points(self):
        return sum(map(lambda story: (story.points_value() if story.status == Story.STATUS_DONE else 0), self.stories.all()))

    def max_points(self):
        logs = self.points_log.all()
        if len(logs) == 0:
            return None
        return reduce(lambda x, y: max(x, y.points_total), logs, 0)

    def starting_points(self):
        for p in self.points_log.all():
            if p.date == self.start_date:
                return p.points_total
        return None

    def daysLeft(self):
        try:
            today = date.today()
            if self.start_date <= today and self.end_date >= today:
                return (self.end_date - today).days
        except:
            pass
        return None

    def stats():
        points = 0
        stories = 0
        for story in stories:
            stories += 1
            points += story.points
        return (stories, points)

    def get_absolute_url(self):
        return reverse('iteration', kwargs={'group_slug': self.project.slug, 'iteration_id': self.id})

    class Meta:
        ordering = ["-default_iteration", "end_date"]

    def __unicode__(self):
        return "%s / %s" % (self.project.name, self.name)


class Epic(models.Model):

    """Represents an epic in your backlog."""
    local_id = models.IntegerField()
    summary = models.TextField()
    parent = models.ForeignKey('self', related_name="children", null=True,
                               verbose_name="Parent Epic", help_text="What epic does this one belong within?", )
    detail = models.TextField(blank=True)
    points = models.CharField('points', max_length=4, default="?", blank=True,
                              help_text="Rough size of this epic (including size of sub-epics or stories).  Enter ? to specify no sizing.")
    project = models.ForeignKey(Project, related_name="epics")
    status = models.IntegerField(
        max_length=2, choices=STATUS_CHOICES, default=1)
    order = models.IntegerField(max_length=5, default=5000)
    archived = models.BooleanField(
        default=False, help_text="Archived epics are generally hidden and their points don't count towards the project.")

    def save(self, *args, **kwargs):
        if self.parent == self:
            self.parent = None
        super(Epic, self).save(*args, **kwargs)

    def stories_by_rank(self):
        return self.stories.all().order_by("rank")

    def short_name(self):
        if self.parent_id:
            return "%s / #E%d" % (self.parent.short_name(), self.local_id)
        return "#E%d" % (self.local_id)

    def full_name(self):
        if self.parent_id:
            return "%s / #E%d %s" % (self.parent.full_name(), self.local_id, self.summary)
        return "#E%d %s" % (self.local_id, self.summary)

    def normalized_points_value(self):
        "Returns the point value of this epic, minus the point value of the stories within it, minimum of 0"
        pv = self.points_value()
        for story in self.stories.all():
            pv -= story.points_value()
        for epic in self.children.all():
            pv -= epic.normalized_points_value()
        return max(pv, 0)

    def points_value(self):
        if self.points.lower() == "inf":
            return 0
        try:
            return float(self.points)
        except:
            return 0

    def getPointsLabel(self):
        result = filter(
            lambda v: v[0] == self.points, Project.POINT_RANGES[self.project.point_scale_type])
        if len(result) > 0:
            return result[0][1]
        return self.points

    def __unicode__(self):
        if self.local_id is None:
            local_id = -1
        else:
            local_id = self.local_id
        return u"Epic %d %s" % (local_id, self.summary)

    class Meta:
        ordering = ['order']


class Story(models.Model):
    STATUS_TODO = 1
    STATUS_DOING = 2
    STATUS_REVIEWING = 3
    STATUS_DONE = 4
    rank = models.IntegerField()
    board_rank = models.IntegerField(default=0)
    summary = models.TextField()
    local_id = models.IntegerField()
    detail = models.TextField(blank=True)
    creator = models.ForeignKey(
        User, related_name="created_stories", verbose_name=_('creator'))
    created = models.DateTimeField(_('created'), default=datetime.now)
    modified = models.DateTimeField(_('modified'), default=datetime.now)
    assignee = models.ForeignKey(
        User, related_name="assigned_stories", verbose_name=_('assignee'), null=True, blank=True)
    points = models.CharField('points', max_length=3, default="?", blank=True)
    iteration = models.ForeignKey(Iteration, related_name="stories")
    project = models.ForeignKey(Project, related_name="stories")
    status = models.IntegerField(
        max_length=2, choices=STATUS_CHOICES, default=1)
    category = models.CharField(max_length=25, blank=True, null=True)
    extra_1 = models.TextField(blank=True, null=True)
    extra_2 = models.TextField(blank=True, null=True)
    extra_3 = models.TextField(blank=True, null=True)
    epic = models.ForeignKey(
        Epic, null=True, blank=True, related_name="stories")

    tags_to_delete = []
    tags_to_add = []

    @staticmethod
    def getAssignedStories(user, organization):
        projects = ProjectMember.getProjectsForUser(
            user, organization=organization)
        assigned_stories = []
        for project in projects:
            if project.active and project.organization == organization:
                project_stories = []
                iterations = project.get_current_iterations()
                for iteration in iterations:
                    project_stories = project_stories + \
                        list(iteration.stories.filter(
                            assignee=user).exclude(status=4).select_related())
                    project_stories = project_stories + \
                        list(iteration.stories.filter(
                            tasks__assignee=user).exclude(status=4).select_related())
                if len(project_stories) > 0:
                    assigned_stories = assigned_stories + \
                        [(project, list(set(project_stories)))]
        return assigned_stories

    def story_tags_full(self):
        "Helper function to return queryset of taggings with the tag object preloaded"
        return self.story_tags.all().select_related("tag")

    def statusText(self):
        return STATUS_CHOICES[self.status - 1][1]

    def getPointsLabel(self):
        result = filter(lambda v: v[0] == self.points, self.getPointScale())
        if len(result) > 0:
            return result[0][1]
        return self.points

    def getPointScale(self):
        return Project.POINT_RANGES[self.project.point_scale_type]

    def points_value(self):
        # the float() method understands inf!
        if self.points.lower() == "inf":
            return 0

        try:
            return float(self.points)
        except:
            return 0

    def getExternalLink(self, extra_slug):
        try:
            link = self.external_links.get(extra_slug="basecamp")
        except:
            return None
        return link

    @property
    def tags(self):
        r = ""
        for tag in self.story_tags.all():
            if len(r) > 0:
                r = r + ", "
            r = r + tag.name
        return r

    @tags.setter
    def tags(self, value):
        # print "TAGS SET " + value
        input_tags = re.split('[, ]+', value)
        self.tags_to_delete = []
        self.tags_to_add = []
        # First, find all the tags we need to add.
        for input_tag in input_tags:
            found = False
            for saved_tag in self.story_tags.all():
                if saved_tag.name == input_tag:
                    found = True
            if not found:
                self.tags_to_add.append(input_tag)
        # Next, find the tags we have to delete
        for saved_tag in self.story_tags.all():
            found = False
            for input_tag in input_tags:
                if saved_tag.name == input_tag:
                    found = True
            if not found:
                self.tags_to_delete.append(saved_tag)

    def __unicode__(self):
        return "[%s/#%d] %s" % (self.project.name, self.local_id, self.summary)

    @models.permalink
    def get_absolute_url(self):
        return ('story_permalink', [str(self.id)])
    # def get_absolute_url(self):
    # return (self.iteration.get_absolute_url() + "#story_" + str(self.id))


def tag_callback(sender, instance, **kwargs):

    for tag_to_delete in instance.tags_to_delete:
        tag_to_delete.delete()
    for tag_to_add in instance.tags_to_add:
        tag_to_add = tag_to_add.strip()
        if len(tag_to_add) == 0:
            continue
        tag = None
        try:
            tags = StoryTag.objects.filter(
                project=instance.project, name=tag_to_add)
            if tags.len() > 0:
                tag = tags[0]
        except:
            pass

        if tag is None:
            tag = StoryTag(project=instance.project, name=tag_to_add)
            tag.save()

        tagging = StoryTagging(tag=tag, story=instance)
        tagging.save()
    instance.tags_to_delete = []
    instance.tags_to_add = []

models.signals.post_save.connect(tag_callback, sender=Story)


class Task(models.Model):
    story = models.ForeignKey(Story, related_name="tasks")
    summary = models.TextField(blank=True)
    assignee = models.ForeignKey(
        User, related_name="assigned_tasks", verbose_name=_('assignee'), null=True, blank=True)
    complete = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    def getExternalLink(self, extra_slug):
        try:
            link = self.external_links.get(extra_slug="basecamp")
        except:
            return None
        return link

    def __unicode__(self):
        return "[%s/#%d] Task: %s" % (self.story.project.name, self.story.local_id, self.summary)

    class Meta:
        ordering = ['order']


class StoryTag(models.Model):
    project = models.ForeignKey(Project, related_name="tags")
    name = models.CharField('name', max_length=32)

    def __unicode__(self):
        return "[%s] %s" % (self.project.name, self.name)


class StoryTagging(models.Model):
    tag = models.ForeignKey(StoryTag, related_name="stories")
    story = models.ForeignKey(Story, related_name="story_tags")

    @property
    def name(self):
        return self.tag.name


class ProjectMember(models.Model):
    project = models.ForeignKey(
        Project, related_name="members", verbose_name=_('project'))
    user = models.ForeignKey(
        User, related_name="projects", verbose_name=_('user'))

    away = models.BooleanField(_('away'), default=False)
    away_message = models.CharField(_('away_message'), max_length=500)
    away_since = models.DateTimeField(_('away since'), default=datetime.now)

    def __str__(self):
        return "ProjectMember: %s " % self.user.username

    @staticmethod
    def getProjectsForUser(user, organization=None):
        """ This gets all a user's projects, including ones they have access to via teams. """
        query = ProjectMember.objects.filter(user=user)
        if organization:
            query = query.filter(project__organization=organization)
        user_projects = [pm.project for pm in query.select_related()]

        team_query = Team.objects.filter(members=user)
        if organization:
            team_query = team_query.filter(organization=organization)
        team_projects = [team.projects.select_related('organization')
                         for team in team_query]
        for project_list in team_projects:
            user_projects = user_projects + list(project_list)
        return list(set(user_projects))
