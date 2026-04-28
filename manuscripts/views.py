from rest_framework.permissions import IsAdminUser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Manuscript, Review
from .emails import send_acceptance_email, send_reviewer_assignment_email, send_review_submitted_email
from .serializers import ManuscriptSerializer
from .emails import send_submission_email
from .utils import assign_reviewer_automatically


class SubmitPaperView(APIView):
    """Author submits paper - auto-assigns reviewer"""
    def post(self, request):
        serializer = ManuscriptSerializer(
            data=request.data,
            context={'request': request}
        )

        if serializer.is_valid():
            manuscript = serializer.save()
            author = manuscript.authors.filter(is_main_author=True).first()

            # 🔹 SEND EMAIL TO AUTHOR
            if author:
                try:
                    send_submission_email(manuscript, author.email)
                except Exception as e:
                    print("Email error:", e)

            # 🔹 AUTO-ASSIGN REVIEWER
            reviewer = assign_reviewer_automatically(manuscript)

            return Response({
                "message": "Paper submitted successfully. Reviewer auto-assigned.",
                "paper_id": str(manuscript.paper_id),
                "status": manuscript.status,
                "assigned_reviewer": reviewer.username if reviewer else None
            }, status=status.HTTP_201_CREATED)

        print("Serializer Errors:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TrackPaperView(APIView):
    """Author tracks paper using paper_id + email (no authentication)"""

    def post(self, request):
        paper_id = request.data.get("paper_id")
        email = request.data.get("email")

        if not paper_id or not email:
            return Response(
                {"error": "paper_id and email required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            manuscript = Manuscript.objects.get(
                paper_id=paper_id,
                authors__email=email
            )

            data = ManuscriptSerializer(manuscript).data

            return Response({
                "message": "Paper found",
                "data": data
            })

        except Manuscript.DoesNotExist:
            return Response(
                {"error": "Invalid paper_id or email"},
                status=status.HTTP_404_NOT_FOUND
            )


class SubmitReviewView(APIView):
    """Admin submits review on behalf of reviewer"""
    permission_classes = [IsAdminUser]

    def post(self, request):
        review_id = request.data.get("review_id")
        decision = request.data.get("decision")
        comments = request.data.get("comments", "")

        if decision not in ['accepted', 'rejected', 'pending']:
            return Response({"error": "Invalid decision"}, status=400)

        try:
            review = Review.objects.get(id=review_id)
            review.decision = decision
            review.comments = comments
            review.save()

            # Notify editor/admin that a review was submitted
            try:
                send_review_submitted_email(review.manuscript)
            except Exception as e:
                print(f"Error sending review-submitted email: {e}")

            return Response({
                "message": "Review submitted",
                "review_id": review.id,
                "decision": decision
            })

        except Review.DoesNotExist:
            return Response({"error": "Review not found"}, status=404)


class FinalDecisionView(APIView):
    """Admin makes final decision on manuscript"""
    permission_classes = [IsAdminUser]

    def post(self, request, manuscript_id):
        decision = request.data.get("decision")

        if decision not in ['accepted', 'rejected', 'revision']:
            return Response({"error": "Invalid decision"}, status=400)

        try:
            manuscript = Manuscript.objects.get(id=manuscript_id)
            manuscript.final_decision = decision
            manuscript.status = decision
            manuscript.save()

            author = manuscript.authors.filter(is_main_author=True).first()

            if author and decision == "accepted":
                send_acceptance_email(manuscript, author.email)

            return Response({
                "message": "Final decision applied",
                "decision": decision
            })

        except Manuscript.DoesNotExist:
            return Response({"error": "Manuscript not found"}, status=404)