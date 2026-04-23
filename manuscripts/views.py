from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser  # ✅ ADD THIS
from .utils import assign_reviewer_automatically
from .models import Manuscript, Review
from .emails import send_acceptance_email
from .serializers import ManuscriptSerializer
from .emails import send_submission_email
from .emails import send_review_submitted_email
from .emails import send_final_decision_email
class SubmitPaperView(APIView):
    def post(self, request):
        serializer = ManuscriptSerializer(
            data=request.data,
            context={'request': request}
        )

        # ✅ validate data
        if serializer.is_valid():

            # 🔹 save manuscript
            manuscript = serializer.save()

            # 🔹 AUTO ASSIGN REVIEWER
            reviewer = assign_reviewer_automatically(manuscript)

            # 🔹 GET MAIN AUTHOR EMAIL
            author = manuscript.authors.filter(is_main_author=True).first()

            # 🔹 SEND EMAIL TO AUTHOR
            if author:
                try:
                    send_submission_email(manuscript, author.email)
                except Exception as e:
                    print("Email error:", e)  # avoid crash

            # 🔹 RESPONSE
            return Response({
                "message": "Submitted successfully",
                "paper_id": str(manuscript.paper_id),
                "assigned_reviewer": reviewer.username if reviewer else None
            }, status=status.HTTP_201_CREATED)

        # ❌ ERROR HANDLING
        print("Serializer Errors:", serializer.errors)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TrackPaperView(APIView):
    """
    Track paper using paper_id + email
    """

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
class AssignReviewersView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, manuscript_id):
        reviewer_ids = request.data.get("reviewers", [])

        try:
            manuscript = Manuscript.objects.get(id=manuscript_id)

            created_reviews = []

            for reviewer_id in reviewer_ids:
                review, created = Review.objects.get_or_create(
                    manuscript=manuscript,
                    reviewer_id=reviewer_id
                )

                if created:
                    created_reviews.append(review.id)

            return Response({
                "message": "Reviewers assigned",
                "assigned_reviews": created_reviews
            })

        except Manuscript.DoesNotExist:
            return Response({"error": "Manuscript not found"}, status=404)

class UpdateStatusView(APIView):
    permission_classes = [IsAdminUser]

    def patch(self, request, pk):
        try:
            manuscript = Manuscript.objects.get(id=pk)

            status_value = request.data.get("status")

            if status_value not in ['submitted', 'under_review', 'accepted', 'rejected']:
                return Response({"error": "Invalid status"}, status=400)

            manuscript.status = status_value
            manuscript.save()

            return Response({"message": "Status updated"})

        except Manuscript.DoesNotExist:
            return Response({"error": "Not found"}, status=404)


class UserDashboardView(APIView):
    permission_classes = []

    def get(self, request):
        user_email = request.user.email

        manuscripts = Manuscript.objects.filter(
            authors__email=user_email
        ).distinct().order_by('-created_at')

        data = ManuscriptSerializer(manuscripts, many=True).data

        return Response(data)


class ReviewerDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # 🔒 Only reviewer allowed
        if user.role != 'reviewer':
            return Response({"error": "Only reviewers allowed"}, status=403)

        # 🔹 get reviews assigned to this reviewer
        reviews = Review.objects.filter(reviewer=user)

        response_data = []

        for review in reviews:
            manuscript = review.manuscript

            response_data.append({
                "review_id": review.id,
                "paper_id": manuscript.paper_id,
                "title": manuscript.title,
                "status": manuscript.status,
                "review_status": review.decision
            })

        return Response(response_data)

class SubmitReviewView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, review_id):
        user = request.user

        try:
            review = Review.objects.get(id=review_id, reviewer=user)

            decision = request.data.get("decision")
            comments = request.data.get("comments")

            if decision not in ['accepted', 'rejected']:
                return Response({"error": "Invalid decision"}, status=400)

            review.decision = decision
            review.comments = comments
            send_review_submitted_email(review.manuscript)

            return Response({"message": "Review submitted"})

        except Review.DoesNotExist:
            return Response({"error": "Review not found"}, status=404)
class FinalDecisionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, manuscript_id):
        user = request.user

        if user.role != 'editor':
            return Response({"error": "Only editor allowed"}, status=403)

        try:
            manuscript = Manuscript.objects.get(id=manuscript_id)

            decision = request.data.get("decision")

            if decision not in ['accepted', 'rejected', 'revision']:
                return Response({"error": "Invalid decision"}, status=400)

            # 🔥 SAVE DECISION
            manuscript.final_decision = decision
            manuscript.status = decision
            manuscript.save()

            # ✅ ADD EMAIL LOGIC HERE 👇
            author = manuscript.authors.filter(is_main_author=True).first()

            if author and decision == "accepted":
                send_acceptance_email(manuscript, author.email)

            return Response({
                "message": "Final decision applied",
                "decision": decision
            })

        except Manuscript.DoesNotExist:
            return Response({"error": "Manuscript not found"}, status=404)
class EditorDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        if user.role != 'editor':
            return Response({"error": "Only editor allowed"}, status=403)

        manuscripts = Manuscript.objects.all().order_by('-created_at')

        response_data = []

        for manuscript in manuscripts:
            reviews = manuscript.reviews.all()

            review_data = []
            for r in reviews:
                review_data.append({
                    "reviewer": r.reviewer.username,
                    "decision": r.decision,
                    "comments": r.comments
                })

            response_data.append({
                "paper_id": manuscript.paper_id,
                "title": manuscript.title,
                "status": manuscript.status,
                "final_decision": manuscript.final_decision,
                "reviews": review_data
            })

        return Response(response_data)