from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model

from manuscripts.models import Review, Manuscript

User = get_user_model()


def build_assigned_papers(user, request):
    reviews = Review.objects.filter(reviewer=user).select_related("manuscript")

    assigned_papers = []
    for review in reviews:
        manuscript = review.manuscript
        assigned_papers.append({
            "review_id": review.id,
            "review_code": review.review_code,
            "paper_id": manuscript.paper_id,
            "title": manuscript.title,
            "status": manuscript.status,
            "decision": review.decision,
            "file_url": request.build_absolute_uri(manuscript.file.url) if manuscript.file else None,
        })

    return assigned_papers


def serialize_reviewer(user):
    return {
        "id": user.username,
        "email": user.email,
        "name": user.get_full_name() or user.username,
        "institute_name": user.institute_name,
        "department": user.department,
        "designation": user.designation,
        "expertise_area": user.expertise_area,
        "phone_number": user.phone_number,
    }


class LoginView(APIView):
    def post(self, request):
        reviewer_id = request.data.get("reviewer_id")
        paper_id = request.data.get("paper_id")
        email = request.data.get("email")

        if reviewer_id or paper_id or email:
            if reviewer_id:
                if not email:
                    return Response(
                        {"error": "reviewer_id and email are required"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                user = User.objects.filter(username=reviewer_id, email=email, role="reviewer").first()

                if not user:
                    return Response(
                        {"error": "Invalid reviewer ID or email"},
                        status=status.HTTP_401_UNAUTHORIZED,
                    )

                token, _ = Token.objects.get_or_create(user=user)

                return Response({
                    "message": "Reviewer login successful",
                    "token": token.key,
                    "type": "reviewer",
                    "reviewer": serialize_reviewer(user),
                    "assigned_papers": build_assigned_papers(user, request),
                })

            if paper_id:
                if not email:
                    return Response(
                        {"error": "paper_id and email are required"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                manuscript = Manuscript.objects.filter(paper_id=paper_id, authors__email=email).distinct().first()

                if not manuscript:
                    return Response(
                        {"error": "Invalid paper ID or email"},
                        status=status.HTTP_401_UNAUTHORIZED,
                    )

                author = manuscript.authors.filter(email=email).first()

                return Response({
                    "message": "Author login successful",
                    "type": "author",
                    "author": {
                        "name": author.name if author else None,
                        "email": email,
                        "paper_id": manuscript.paper_id,
                    },
                    "paper": {
                        "paper_id": manuscript.paper_id,
                        "title": manuscript.title,
                        "status": manuscript.status,
                        "final_decision": manuscript.final_decision,
                        "file_url": request.build_absolute_uri(manuscript.file.url) if manuscript.file else None,
                        "authors": [
                            {
                                "name": item.name,
                                "email": item.email,
                                "mobile": item.mobile,
                                "is_main_author": item.is_main_author,
                            }
                            for item in manuscript.authors.all()
                        ],
                    },
                })

        return Response(
            {"error": "paper_id + email for author or reviewer_id + email for reviewer are required"},
            status=status.HTTP_400_BAD_REQUEST,
        )


class ReviewerLoginView(APIView):
    def post(self, request):
        return LoginView().post(request)