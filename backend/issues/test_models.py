"""
Tests for Issue model and Kanban functionality.
"""

import pytest
from issues.models import Issue, Label


@pytest.mark.django_db
class TestIssueModel:
    """Test Issue model functionality."""

    def test_create_issue(self, workspace, project, user):
        """Test creating an issue."""
        issue = Issue.objects.create(
            workspace=workspace,
            project=project,
            title='Test Issue',
            description='Test description',
            reporter=user,
            status=Issue.TODO
        )

        assert issue.title == 'Test Issue'
        assert issue.project == project
        assert issue.reporter == user
        assert issue.status == Issue.TODO

    def test_auto_generated_identifier(self, workspace, project, user):
        """Test issue identifier is auto-generated."""
        issue = Issue.objects.create(
            workspace=workspace,
            project=project,
            title='First Issue',
            reporter=user
        )

        assert issue.identifier == 'TEST-1'

        # Create second issue
        issue2 = Issue.objects.create(
            workspace=workspace,
            project=project,
            title='Second Issue',
            reporter=user
        )

        assert issue2.identifier == 'TEST-2'

    def test_issue_status_choices(self, issue):
        """Test issue status transitions."""
        assert issue.status == Issue.TODO

        # Move to in progress
        issue.status = Issue.IN_PROGRESS
        issue.save()
        assert issue.status == Issue.IN_PROGRESS

        # Move to done
        issue.status = Issue.DONE
        issue.save()
        assert issue.status == Issue.DONE

    def test_issue_priority(self, workspace, project, user):
        """Test issue priority levels."""
        issue = Issue.objects.create(
            workspace=workspace,
            project=project,
            title='Urgent Issue',
            reporter=user,
            priority=Issue.URGENT
        )

        assert issue.priority == Issue.URGENT

    def test_issue_assignment(self, issue, user):
        """Test assigning issues to users."""
        assert issue.assignee is None

        issue.assignee = user
        issue.save()

        assert issue.assignee == user

    def test_issue_labels(self, issue, label):
        """Test adding labels to issues."""
        issue.labels.add(label)

        assert label in issue.labels.all()
        assert issue in label.issues.all()

    def test_parent_child_issues(self, workspace, project, user, issue):
        """Test parent-child issue relationships (sub-issues)."""
        sub_issue = Issue.objects.create(
            workspace=workspace,
            project=project,
            title='Sub Issue',
            reporter=user,
            parent=issue
        )

        assert sub_issue.parent == issue
        assert sub_issue in issue.sub_issues.all()

    def test_issue_string_representation(self, issue):
        """Test issue string representation."""
        assert str(issue) == 'TEST-1 - Test Issue'


@pytest.mark.django_db
class TestLabelModel:
    """Test Label model functionality."""

    def test_create_label(self, workspace):
        """Test creating a label."""
        label = Label.objects.create(
            workspace=workspace,
            name='Bug',
            description='Bug fixes',
            color='#FF0000'
        )

        assert label.name == 'Bug'
        assert label.color == '#FF0000'

    def test_label_string_representation(self, label):
        """Test label string representation."""
        assert str(label) == 'Bug'
