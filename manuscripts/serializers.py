from rest_framework import serializers
from .models import Manuscript, Author
import json


class ManuscriptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manuscript
        fields = '__all__'

    def create(self, validated_data):
        request = self.context.get('request')

        # 🔹 get authors from request directly
        authors_data = request.data.get('authors')

        # 🔹 convert string → python list
        if isinstance(authors_data, str):
            authors_data = json.loads(authors_data)

        # 🔹 remove authors if accidentally present
        validated_data.pop('authors', None)

        # 🔹 create manuscript
        manuscript = Manuscript.objects.create(**validated_data)

        # 🔹 create authors
        if authors_data:
            for author in authors_data:
                Author.objects.create(
                    manuscript=manuscript,
                    name=author.get('name'),
                    email=author.get('email'),
                    mobile=author.get('mobile'),
                    is_main_author=author.get('is_main_author', False)
                )

        return manuscript

from rest_framework import serializers
from .models import Manuscript, Author, Review


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ['name', 'email']


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['decision', 'comments']


class ManuscriptSerializer(serializers.ModelSerializer):
    authors = AuthorSerializer(many=True, read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)

    class Meta:
        model = Manuscript
        fields = '__all__'