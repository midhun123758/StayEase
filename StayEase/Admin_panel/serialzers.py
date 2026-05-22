from Base_Panel.models import HostelDocument

from Base_Panel.serilalizers import HostelSerializer

from App.serializer import Profile

from rest_framework import serializers


class HostelDocumentSerializer(

    serializers.ModelSerializer

):

    pdf_key = serializers.SerializerMethodField()


    uploaded_by = Profile(

        read_only=True

    )


    hostel = HostelSerializer(

        read_only=True

    )


    class Meta:

        model = HostelDocument

        fields = "__all__"


    def get_pdf_key(self, obj):

        return obj.file_url.split(".com/")[-1]