from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings


def _get_from_email():
    """Return the configured sender email address."""
    return getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@journal.com')


# ✅ 1. Submission Email (HTML format)
def send_submission_email(manuscript, author_email):
    subject = "Paper Submission Successful"
    from_email = _get_from_email()

    # Plain-text fallback
    text_content = f"""\
Dear Author,

Your paper has been submitted successfully.

Paper ID: {manuscript.paper_id}
Title: {manuscript.title}

Your manuscript has been received and will undergo an initial review by our editorial team.
You will be notified once a reviewer has been assigned.

You can track your paper status anytime using your Paper ID and registered email address.

Thank you for choosing our journal.

Warm regards,
Editorial Team
"""

    # Professional HTML email
    html_content = f"""\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin:0; padding:0; background-color:#f4f6f9; font-family:'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background-color:#f4f6f9; padding:40px 0;">
    <tr>
      <td align="center">
        <table role="presentation" width="600" cellspacing="0" cellpadding="0" style="background-color:#ffffff; border-radius:12px; overflow:hidden; box-shadow:0 4px 24px rgba(0,0,0,0.08);">

          <!-- Header -->
          <tr>
            <td style="background: linear-gradient(135deg, #1a73e8, #0d47a1); padding:32px 40px; text-align:center;">
              <h1 style="margin:0; color:#ffffff; font-size:24px; font-weight:600; letter-spacing:0.5px;">
                ✅ Paper Submission Successful
              </h1>
            </td>
          </tr>

          <!-- Body -->
          <tr>
            <td style="padding:36px 40px 20px;">
              <p style="margin:0 0 20px; color:#333333; font-size:16px; line-height:1.6;">
                Dear Author,
              </p>
              <p style="margin:0 0 24px; color:#555555; font-size:15px; line-height:1.7;">
                We are pleased to confirm that your manuscript has been
                <strong style="color:#1a73e8;">successfully submitted</strong>
                to our journal. Below are your submission details:
              </p>

              <!-- Details Card -->
              <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background-color:#f0f5ff; border-radius:8px; border-left:4px solid #1a73e8; margin-bottom:28px;">
                <tr>
                  <td style="padding:20px 24px;">
                    <table role="presentation" width="100%" cellspacing="0" cellpadding="0">
                      <tr>
                        <td style="padding:6px 0; color:#666666; font-size:13px; text-transform:uppercase; letter-spacing:0.5px; width:100px;">Paper ID</td>
                        <td style="padding:6px 0; color:#1a73e8; font-size:16px; font-weight:700;">{manuscript.paper_id}</td>
                      </tr>
                      <tr>
                        <td style="padding:6px 0; color:#666666; font-size:13px; text-transform:uppercase; letter-spacing:0.5px;">Title</td>
                        <td style="padding:6px 0; color:#222222; font-size:15px; font-weight:600;">{manuscript.title}</td>
                      </tr>
                      <tr>
                        <td style="padding:6px 0; color:#666666; font-size:13px; text-transform:uppercase; letter-spacing:0.5px;">Status</td>
                        <td style="padding:6px 0;">
                          <span style="display:inline-block; background-color:#e8f5e9; color:#2e7d32; font-size:12px; font-weight:600; padding:4px 12px; border-radius:20px; text-transform:uppercase;">
                            Submitted
                          </span>
                        </td>
                      </tr>
                    </table>
                  </td>
                </tr>
              </table>

              <!-- Next Steps -->
              <p style="margin:0 0 12px; color:#333333; font-size:15px; font-weight:600;">
                📋 What happens next?
              </p>
              <ol style="margin:0 0 28px; padding-left:20px; color:#555555; font-size:14px; line-height:2;">
                <li>Our editorial team will perform an initial screening of your manuscript.</li>
                <li>A qualified reviewer will be assigned for peer review.</li>
                <li>You will receive email updates at each stage of the process.</li>
              </ol>

              <p style="margin:0 0 24px; color:#555555; font-size:14px; line-height:1.7;">
                You can track your paper status anytime using your
                <strong>Paper ID</strong> and <strong>registered email address</strong>
                on our tracking portal.
              </p>

              <!-- Divider -->
              <hr style="border:none; border-top:1px solid #e0e0e0; margin:24px 0;">

              <p style="margin:0; color:#888888; font-size:13px; line-height:1.6;">
                If you have any questions, please don't hesitate to contact our editorial office.
              </p>
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="background-color:#fafafa; padding:20px 40px; text-align:center; border-top:1px solid #eeeeee;">
              <p style="margin:0; color:#999999; font-size:12px;">
                &copy; 2026 Journal Editorial System &bull; All rights reserved
              </p>
              <p style="margin:6px 0 0; color:#bbbbbb; font-size:11px;">
                This is an automated notification. Please do not reply to this email.
              </p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>
"""

    msg = EmailMultiAlternatives(subject, text_content, from_email, [author_email])
    msg.attach_alternative(html_content, "text/html")
    msg.send(fail_silently=False)


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
        from_email=_get_from_email(),
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
        from_email=_get_from_email(),
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
        from_email=_get_from_email(),
        recipient_list=[author_email],
    )


# ✅ 5. Acceptance Email
def send_acceptance_email(manuscript, author_email):
    send_mail(
        subject="Paper Accepted",
        message=f"Your paper {manuscript.paper_id} is accepted",
        from_email=_get_from_email(),
        recipient_list=[author_email],
    )