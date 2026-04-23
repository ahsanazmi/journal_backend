from django.core.mail import send_mail


# ✅ 1. Submission Email
def send_submission_email(manuscript, author_email):
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
        from_email="your_email@gmail.com",
        recipient_list=[author_email],
    )


# ✅ 2. Reviewer Assigned Email
def send_reviewer_assignment_email(manuscript, reviewer_email):
    send_mail(
        subject="New Paper Assigned",
        message=f"""
Dear Reviewer,

A new paper has been assigned to you.

Paper ID: {manuscript.paper_id}
Title: {manuscript.title}

Please login and review.

Regards,
Editorial Team
""",
        from_email="your_email@gmail.com",
        recipient_list=[reviewer_email],
    )


# ✅ 3. Review Submitted Email (to editor)
def send_review_submitted_email(manuscript):
    send_mail(
        subject="Review Submitted",
        message=f"""
A review has been submitted.

Paper ID: {manuscript.paper_id}
Title: {manuscript.title}

Please check and take final decision.
""",
        from_email="your_email@gmail.com",
        recipient_list=["editor@email.com"],
    )


# ✅ 4. Final Decision Email
def send_final_decision_email(manuscript, author_email, decision):
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
        from_email="your_email@gmail.com",
        recipient_list=[author_email],
    )