"""
Webhook Handlers for Integrations
"""

import hashlib
import hmac
import json
import logging
from typing import Dict, Any
from django.utils import timezone
from .models import Integration, WebhookDelivery

logger = logging.getLogger(__name__)


class WebhookHandler:
    """Base webhook handler."""

    def __init__(self, integration: Integration):
        self.integration = integration

    def validate_signature(self, payload: bytes, signature: str, secret: str) -> bool:
        """Validate webhook signature."""
        raise NotImplementedError

    def handle(self, event_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle webhook event."""
        raise NotImplementedError


class GitHubWebhookHandler(WebhookHandler):
    """GitHub webhook handler."""

    def validate_signature(self, payload: bytes, signature: str, secret: str) -> bool:
        """Validate GitHub webhook signature."""
        if not signature or not secret:
            return False

        # GitHub sends signature as 'sha256=<hash>'
        expected_signature = 'sha256=' + hmac.new(
            secret.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(signature, expected_signature)

    def handle(self, event_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle GitHub webhook event."""
        logger.info(f"Handling GitHub event: {event_type}")

        result = {'success': False, 'message': '', 'data': {}}

        try:
            if event_type == 'push':
                result = self._handle_push(payload)
            elif event_type == 'pull_request':
                result = self._handle_pull_request(payload)
            elif event_type == 'issues':
                result = self._handle_issue(payload)
            elif event_type == 'issue_comment':
                result = self._handle_issue_comment(payload)
            elif event_type == 'pull_request_review':
                result = self._handle_pr_review(payload)
            else:
                result['message'] = f"Unhandled event type: {event_type}"

        except Exception as e:
            logger.error(f"Error handling GitHub webhook: {str(e)}")
            result['message'] = str(e)

        return result

    def _handle_push(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle GitHub push event."""
        commits = payload.get('commits', [])
        branch = payload.get('ref', '').split('/')[-1]
        repository = payload.get('repository', {}).get('full_name', '')

        return {
            'success': True,
            'message': f"Processed {len(commits)} commits to {branch} in {repository}",
            'data': {
                'commits': len(commits),
                'branch': branch,
                'repository': repository,
            }
        }

    def _handle_pull_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle GitHub pull request event."""
        action = payload.get('action', '')
        pr = payload.get('pull_request', {})
        pr_number = pr.get('number', 0)
        title = pr.get('title', '')

        return {
            'success': True,
            'message': f"Pull request #{pr_number} {action}: {title}",
            'data': {
                'action': action,
                'pr_number': pr_number,
                'title': title,
            }
        }

    def _handle_issue(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle GitHub issue event."""
        action = payload.get('action', '')
        issue = payload.get('issue', {})
        issue_number = issue.get('number', 0)
        title = issue.get('title', '')

        return {
            'success': True,
            'message': f"Issue #{issue_number} {action}: {title}",
            'data': {
                'action': action,
                'issue_number': issue_number,
                'title': title,
            }
        }

    def _handle_issue_comment(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle GitHub issue comment event."""
        action = payload.get('action', '')
        issue = payload.get('issue', {})
        comment = payload.get('comment', {})

        return {
            'success': True,
            'message': f"Comment {action} on issue #{issue.get('number', 0)}",
            'data': {
                'action': action,
                'issue_number': issue.get('number', 0),
                'comment_id': comment.get('id', 0),
            }
        }

    def _handle_pr_review(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle GitHub pull request review event."""
        action = payload.get('action', '')
        pr = payload.get('pull_request', {})
        review = payload.get('review', {})

        return {
            'success': True,
            'message': f"Review {action} on PR #{pr.get('number', 0)}",
            'data': {
                'action': action,
                'pr_number': pr.get('number', 0),
                'review_state': review.get('state', ''),
            }
        }


class JiraWebhookHandler(WebhookHandler):
    """Jira webhook handler."""

    def validate_signature(self, payload: bytes, signature: str, secret: str) -> bool:
        """Validate Jira webhook signature."""
        if not signature or not secret:
            return False

        # Jira uses HMAC-SHA256
        expected_signature = hmac.new(
            secret.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(signature, expected_signature)

    def handle(self, event_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Jira webhook event."""
        logger.info(f"Handling Jira event: {event_type}")

        result = {'success': False, 'message': '', 'data': {}}

        try:
            if event_type == 'jira:issue_created':
                result = self._handle_issue_created(payload)
            elif event_type == 'jira:issue_updated':
                result = self._handle_issue_updated(payload)
            elif event_type == 'jira:issue_deleted':
                result = self._handle_issue_deleted(payload)
            elif event_type == 'comment_created':
                result = self._handle_comment_created(payload)
            else:
                result['message'] = f"Unhandled event type: {event_type}"

        except Exception as e:
            logger.error(f"Error handling Jira webhook: {str(e)}")
            result['message'] = str(e)

        return result

    def _handle_issue_created(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Jira issue created event."""
        issue = payload.get('issue', {})
        key = issue.get('key', '')
        fields = issue.get('fields', {})
        summary = fields.get('summary', '')

        return {
            'success': True,
            'message': f"Jira issue created: {key} - {summary}",
            'data': {
                'key': key,
                'summary': summary,
            }
        }

    def _handle_issue_updated(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Jira issue updated event."""
        issue = payload.get('issue', {})
        key = issue.get('key', '')
        changelog = payload.get('changelog', {})

        return {
            'success': True,
            'message': f"Jira issue updated: {key}",
            'data': {
                'key': key,
                'changes': len(changelog.get('items', [])),
            }
        }

    def _handle_issue_deleted(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Jira issue deleted event."""
        issue = payload.get('issue', {})
        key = issue.get('key', '')

        return {
            'success': True,
            'message': f"Jira issue deleted: {key}",
            'data': {
                'key': key,
            }
        }

    def _handle_comment_created(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Jira comment created event."""
        comment = payload.get('comment', {})
        issue = payload.get('issue', {})

        return {
            'success': True,
            'message': f"Comment added to {issue.get('key', '')}",
            'data': {
                'issue_key': issue.get('key', ''),
                'comment_id': comment.get('id', ''),
            }
        }


class SlackWebhookHandler(WebhookHandler):
    """Slack webhook handler."""

    def validate_signature(self, payload: bytes, signature: str, secret: str) -> bool:
        """Validate Slack webhook signature."""
        if not signature or not secret:
            return False

        # Slack uses a different signature format
        # signature format: v0=<hash>
        if not signature.startswith('v0='):
            return False

        expected_signature = 'v0=' + hmac.new(
            secret.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(signature, expected_signature)

    def handle(self, event_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Slack webhook event."""
        logger.info(f"Handling Slack event: {event_type}")

        result = {'success': False, 'message': '', 'data': {}}

        try:
            # Handle URL verification challenge
            if payload.get('type') == 'url_verification':
                return {
                    'success': True,
                    'message': 'URL verification successful',
                    'data': {'challenge': payload.get('challenge', '')},
                }

            # Handle event callback
            if payload.get('type') == 'event_callback':
                event = payload.get('event', {})
                event_type = event.get('type', '')

                if event_type == 'message':
                    result = self._handle_message(event)
                elif event_type == 'reaction_added':
                    result = self._handle_reaction(event)
                elif event_type == 'channel_created':
                    result = self._handle_channel_created(event)
                else:
                    result['message'] = f"Unhandled event type: {event_type}"
            else:
                result['message'] = f"Unhandled payload type: {payload.get('type')}"

        except Exception as e:
            logger.error(f"Error handling Slack webhook: {str(e)}")
            result['message'] = str(e)

        return result

    def _handle_message(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Slack message event."""
        channel = event.get('channel', '')
        user = event.get('user', '')
        text = event.get('text', '')

        return {
            'success': True,
            'message': f"Message received in channel {channel}",
            'data': {
                'channel': channel,
                'user': user,
                'text': text,
            }
        }

    def _handle_reaction(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Slack reaction added event."""
        reaction = event.get('reaction', '')
        user = event.get('user', '')

        return {
            'success': True,
            'message': f"Reaction :{reaction}: added by {user}",
            'data': {
                'reaction': reaction,
                'user': user,
            }
        }

    def _handle_channel_created(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Slack channel created event."""
        channel = event.get('channel', {})
        channel_name = channel.get('name', '')

        return {
            'success': True,
            'message': f"Channel created: #{channel_name}",
            'data': {
                'channel_id': channel.get('id', ''),
                'channel_name': channel_name,
            }
        }


def get_webhook_handler(integration: Integration) -> WebhookHandler:
    """Get appropriate webhook handler for integration type."""
    handlers = {
        'github': GitHubWebhookHandler,
        'jira': JiraWebhookHandler,
        'slack': SlackWebhookHandler,
    }

    handler_class = handlers.get(integration.integration_type)
    if not handler_class:
        raise ValueError(f"No handler for integration type: {integration.integration_type}")

    return handler_class(integration)
