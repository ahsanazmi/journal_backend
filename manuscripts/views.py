from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser  # ✅ ADD THIS

from .models import Manuscript
from .serializers import ManuscriptSerializer


class SubmitPaperView(APIView):
    def post(self, request):
        serializer = ManuscriptSerializer(
            data=request.data,
            context={'request': request}
        )

        if serializer.is_valid():
            manuscript = serializer.save()

            return Response({
                "message": "Submitted successfully",
                "paper_id": str(manuscript.paper_id)
            })

        # 🔥 PRINT ERROR
        print(serializer.errors)

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

        # 🔹 check role
        if user.role != 'reviewer':
            return Response(
                {"error": "Only reviewers allowed"},
                status=403
            )

        # 🔹 get assigned reviews
        reviews = Review.objects.filter(reviewer=user)

        # 🔹 get manuscripts
        manuscripts = [r.manuscript for r in reviews]

        data = ManuscriptSerializer(manuscripts, many=True).data

        return Response(data)