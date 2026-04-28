from django.core.mail import EmailMessage, send_mail
from django.conf import settings


# ✅ 1. Submission Email
def send_submission_email(manuscript, author_email):
    try:
        send_mail(
            subject="Paper Submitted Successfully",
            message=f"""
Dear Author,

Your paper has been submitted successfully.

Paper ID: {manuscript.paper_id}
Title: {manuscript.title}

You can track your paper using Paper ID + Email.

Regards,
Editorial Team
""",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[author_email],
        )
    except Exception as e:
        # Fallback for development: log to console so admin can see the message
        print(f"Failed to send submission email to {author_email}: {e}")
        print("--- EMAIL (fallback) ---")
        print(f"To: {author_email}")
        print("Subject: Paper Submitted Successfully")
        print(f"Paper ID: {manuscript.paper_id}")
        print(f"Title: {manuscript.title}")
        print("--- END EMAIL ---")


# ✅ 2. Reviewer Assigned Email
def send_reviewer_assignment_email(manuscript, reviewer_email):
    message = EmailMessage(
        subject="New Paper Assigned for Review",
        body=f"""
Dear Reviewer,

A new paper has been assigned to you for review.

Paper ID: {manuscript.paper_id}
Title: {manuscript.title}

Please review and provide your feedback.

Regards,
Editorial Team
""",
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[reviewer_email],
    )

    if manuscript.file:
        message.attach_file(manuscript.file.path)

    try:
        message.send()
    except Exception as e:
        # log and fallback to console
        print(f"Failed to send reviewer assignment email to {reviewer_email}: {e}")
        print("--- EMAIL (fallback) ---")
        print(f"To: {reviewer_email}")
        print("Subject: New Paper Assigned for Review")
        print(f"Paper ID: {manuscript.paper_id}")
        print(f"Title: {manuscript.title}")
        print("Attachment: attached file path:" , getattr(manuscript.file, 'path', None))
        print("--- END EMAIL ---")


# ✅ 3. Editorial Board Assignment Email
def send_editorial_assignment_email(manuscript, editorial_email, editorial_role):
    try:
        send_mail(
            subject=f"New Task Assigned - {editorial_role}",
            message=f"""
Dear {editorial_role},

A new manuscript has been assigned to you.

Paper ID: {manuscript.paper_id}
Title: {manuscript.title}
Status: {manuscript.status}

Please review and take necessary action.

Regards,
Editorial System
""",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[editorial_email],
        )
    except Exception as e:
        print(f"Failed to send editorial assignment email to {editorial_email}: {e}")


# ✅ 4. Review Submitted Email (to editor)
def send_review_submitted_email(manuscript):
    try:
        send_mail(
            subject="Review Submitted",
            message=f"""
A review has been submitted.

Paper ID: {manuscript.paper_id}
Title: {manuscript.title}

Please check and take final decision.
""",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.DEFAULT_FROM_EMAIL],
        )
    except Exception as e:
        print(f"Failed to send review submitted email: {e}")


# ✅ 5. Final Decision Email
def send_final_decision_email(manuscript, author_email, decision):
    try:
        send_mail(
            subject="Final Decision on Your Paper",
            message=f"""
Dear Author,

Your paper decision is:

Paper ID: {manuscript.paper_id}
Title: {manuscript.title}
Decision: {decision.upper()}

Regards,
Editorial Team
""",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[author_email],
        )
    except Exception as e:
        print(f"Failed to send final decision email to {author_email}: {e}")


def send_acceptance_email(manuscript, author_email):
    try:
        send_mail(
            subject="Paper Accepted",
            message=f"Your paper {manuscript.paper_id} is accepted",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[author_email],
        )
    except Exception as e:
        print(f"Failed to send acceptance email to {author_email}: {e}")


def send_status_update_email(manuscript, author_email, old_status=None, new_status=None):
    """Notify the main author when an admin changes manuscript status."""
    try:
        send_mail(
            subject="Paper Status Updated",
            message=f"""
Dear Author,

Your paper status has been updated.

Paper ID: {manuscript.paper_id}
Title: {manuscript.title}
Previous Status: {old_status or 'N/A'}
Current Status: {new_status or manuscript.status}
Final Decision: {manuscript.final_decision}

You can check the latest status in the tracking portal using Paper ID + Email.

Regards,
Editorial Team
""",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[author_email],
        )
    except Exception as e:
        print(f"Failed to send status update email to {author_email}: {e}")