from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from regsys_api.authsys.models import User
from .models import (
    Track, HackathonTeams, HackathonTeamsMember, HackathonTask, TaskResponse,
    TeamMember
)
from regsys_api.authsys.serializers import UserSerializer
from django.http import JsonResponse
from rest_framework.response import Response
import json


class TrackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Track
        fields = (
            'id', 'name', 'team_min_member', 'team_max_member', 'description', 'closed_date', 'isExpired', 'slug_name',
            'biaya_pendaftaran', 'is_closed', 'slug_image'
        )


class HackathonTeamsMemberSerializer(serializers.ModelSerializer):
    nama = serializers.ReadOnlyField(
        source="user.full_name",
        read_only=True
    )

    email = serializers.ReadOnlyField(
        source="user.email",
        read_only=True
    )

    nomor_id = serializers.ReadOnlyField(
        source="user.nomor_id",
        read_only=True
    )

    tanggal_lahir = serializers.ReadOnlyField(
        source="user.tanggal_lahir",
        read_only=True
    )

    is_confirmed = serializers.ReadOnlyField(
        source="user.is_confirmed",
        read_only=True
    )

    is_vege = serializers.ReadOnlyField(
        source="user.is_vege",
        read_only=True
    )

    alergic = serializers.ReadOnlyField(
        source="user.alergic",
        read_only=True
    )

    last_login = serializers.ReadOnlyField(
        source="user.last_login",
        read_only=True
    )

    date_joined = serializers.ReadOnlyField(
        source="user.date_joined",
        read_only=True
    )

    nomor_telepon = serializers.ReadOnlyField(
        source="user.nomor_telepon",
        read_only=True
    )

    id_line = serializers.ReadOnlyField(
        source="user.id_line",
        read_only=True
    )

    class Meta:
        model = HackathonTeamsMember
        fields = ('nama', 'email', 'nomor_id', 'tanggal_lahir', 'is_vege', 'alergic', 'id_line', 'nomor_telepon',
                  'is_confirmed', 'date_joined', 'last_login')


class HackathonTeamsSerializer(serializers.ModelSerializer):
    # track = TrackSerializer(read_only=True)
    team_leader_name = serializers.SlugRelatedField(
        source='team_leader',
        slug_field='full_name',
        read_only=True,
    )

    team_leader_email = serializers.SlugRelatedField(
        source='team_leader',
        slug_field='email',
        read_only=True,
    )

    class Meta:
        model = HackathonTeams
        fields = (
            'id', 'name', 'team_leader_name', 'team_leader_email', 'institution', 'is_blacklisted'
        )
        read_only_fields = (
            'id', 'team_leader_name', 'team_leader_email', 'institution', 'is_blacklisted'

        )


class TaskResponseSerializer(serializers.ModelSerializer):
    # task_id = HackathonTaskSerializer(source='team')
    # task = HackathonTaskSerializer(read_only=True)

    class Meta:
        model = TaskResponse
        fields = ('id', 'task_id', 'response',
                  'status', 'updated_at', 'is_verified')
        read_only_fields = ('task_id',)


class HackathonTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = HackathonTask
        fields = (
            'id', 'name', 'deadline', 'deskripsi', 'order', 'task_type', 'max_file_upload'
        )


class HackathonTeamsDetailSerializer(serializers.ModelSerializer):
    track = TrackSerializer(read_only=True)
    team_leader_name = serializers.SlugRelatedField(
        source='team_leader', slug_field='full_name', queryset=User.objects.all()
    )
    team_members = HackathonTeamsMemberSerializer(many=True, read_only=True)

    current_task = HackathonTaskSerializer(read_only=True)

    task_list = HackathonTaskSerializer(many=True)

    task_response_list = TaskResponseSerializer(many=True, read_only=True)

    class Meta:
        model = HackathonTeams
        fields = (
            'task_list', 'id', 'task_response_list', 'track', 'name', 'team_leader_name', 'institution',
            'is_blacklisted', 'team_members', 'created_at', 'invitation_token', 'current_task', 'bisa_up_task'
        )
        read_only_fields = (
            'task_list', 'id', 'task_response_list', 'track', 'name', 'team_leader_name', 'institution',
            'is_blacklisted', 'team_members', 'created_at', 'invitation_token', 'current_task', 'bisa_up_task'
        )


class RegisterHackathonTeamSerializer(serializers.Serializer):
    slug_name = serializers.CharField(max_length=50)
    name = serializers.CharField(max_length=100, min_length=3, validators=[
        UniqueValidator(queryset=HackathonTeams.objects.all())])
    team_institution = serializers.CharField(max_length=50)
    alamat_institution = serializers.CharField(max_length=500)
    nama_pembimbing = serializers.CharField(max_length=50)
    no_telp_pembimbing = serializers.CharField(max_length=20)


class AddHackathonTeamMemberSerializer(serializers.Serializer):
    full_name = serializers.CharField(max_length=100)
    email = serializers.EmailField()


class JoinTeamSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=50)


class TeamDetailSerializer(serializers.ModelSerializer):
    kompetisi = TrackSerializer(source='track', read_only=True)

    nama = serializers.CharField(source='name', read_only=True)
    asal = serializers.CharField(source='institution', read_only=True)
    alamat = serializers.CharField(source='alamat_institusi')

    ketua = serializers.SlugRelatedField(
        source='team_leader', slug_field='full_name', queryset=User.objects.all()
    )
    pembimbing = serializers.SerializerMethodField('get_info_pembimbing')
    # anggota = HackathonTeamsMemberSerializer(source='team_members', many=True)
    anggota = serializers.SerializerMethodField('get_info_anggota')

    is_full = serializers.SerializerMethodField('cek_is_full')

    token = serializers.CharField(source='invitation_token', read_only=True)
    ditangguhkan = serializers.BooleanField(
        source='is_blacklisted', read_only=True)

    tasks = serializers.SerializerMethodField('get_info_task')

    # response = TaskResponseSerializer(source='task_response', many=True, read_only=True)

    current_task = HackathonTaskSerializer(read_only=True)

    task_permission = serializers.BooleanField(source='bisa_up_task')

    # task_list = HackathonTaskSerializer(many=True)

    class Meta:
        model = HackathonTeams
        fields = (
            'id', 'is_full',
            'kompetisi', 'nama', 'asal', 'alamat', 'ketua', 'pembimbing', 'anggota',
            'token', 'ditangguhkan', 'created_at', 'tasks', 'current_task', 'task_permission'  # 'tasks'
        )

    # def get_info_task(self, obj):
    #    tasks = TaskResponse.objects.filter(team=obj).all()
    #    return HackathonTaskSerializer(tasks, many=True)

    def get_info_pembimbing(self, obj):
        return {
            'nama': obj.nama_pendamping,
            'telepon': obj.nomor_telepon_pendamping
        }

    def cek_is_full(self, obj):
        return obj.jumlah_member >= obj.track.team_max_member

    def get_info_anggota(self, obj):
        data = []
        queryset = HackathonTeamsMember.objects.filter(
            team=obj).all()
        list_qs = list(queryset.values())
        json_list_all = json.loads("[]")
        for e in queryset:
            if e.user is not None:
                json_list_all.append(json.loads(
                    json.dumps(UserSerializer(e.user).data)
                ))
            else:
                json_list_all.append(json.loads(
                    json.dumps(UserSerializer(e).data)
                ))
        return json_list_all

    def get_info_task(self, obj):
        data = []
        queryset = HackathonTask.objects.filter(
            track=obj.track).order_by('order')

        list_qs = list(queryset.values())

        json_list_all = json.loads("[]")

        for e in queryset:

            json_list = json.loads(
                '{"task" : [], "response": []}'
            )

            qs_response = TaskResponse.objects.filter(team=obj, task=e).first()

            if qs_response:

                json_list["task"] = json.loads(
                    json.dumps(HackathonTaskSerializer(e).data)
                )

                json_list["response"] = json.loads(
                    json.dumps(TaskResponseSerializer(qs_response).data)
                )

            else:
                json_list["task"] = json.loads(
                    json.dumps(HackathonTaskSerializer(e).data)
                )

            json_list_all.append(json_list)

        return json_list_all


"""
    def get_info_task(self, obj):
        queryset = HackathonTask.objects.filter(track=obj.track)
        return json.loads(
            json.dumps(list(HackathonTaskSerializer(queryset, many=True).data))
        )
        """


class PostTaskResponseSerializer(serializers.Serializer):
    team_id = serializers.CharField(max_length=10)
    task_id = serializers.CharField(max_length=10)
    response = serializers.CharField(max_length=500)


class AdminConfirmTask(serializers.Serializer):
    task_res_id = serializers.CharField(max_length=10)
    tolak = serializers.BooleanField()


class AdminTeamDetailSerializer(serializers.ModelSerializer):
    # kompetisi = TrackSerializer(source='track', read_only=True)

    nama = serializers.CharField(source='name', read_only=True)
    asal = serializers.CharField(source='institution', read_only=True)
    alamat = serializers.CharField(source='alamat_institusi')

    ketua = serializers.SlugRelatedField(
        source='team_leader', slug_field='full_name', queryset=User.objects.all()
    )
    pembimbing = serializers.SerializerMethodField('get_info_pembimbing')
    anggota = HackathonTeamsMemberSerializer(source='team_members', many=True)
    # anggota = serializers.SerializerMethodField('get_info_anggota')

    token = serializers.CharField(source='invitation_token', read_only=True)
    ditangguhkan = serializers.BooleanField(
        source='is_blacklisted', read_only=True)

    tasks = serializers.SerializerMethodField('get_info_task')

    # response = TaskResponseSerializer(source='task_response', many=True, read_only=True)

    current_task = HackathonTaskSerializer(read_only=True)

    task_permission = serializers.BooleanField(source='bisa_up_task')

    # task_list = HackathonTaskSerializer(many=True)

    class Meta:
        model = HackathonTeams
        fields = (
            'id',
            'nama', 'asal', 'alamat', 'ketua', 'pembimbing', 'anggota',
            'token', 'ditangguhkan', 'created_at', 'tasks', 'current_task', 'task_permission'  # 'tasks'
        )

    # def get_info_task(self, obj):
    #    tasks = TaskResponse.objects.filter(team=obj).all()
    #    return HackathonTaskSerializer(tasks, many=True)

    def get_info_pembimbing(self, obj):
        return {
            'nama': obj.nama_pendamping,
            'telepon': obj.nomor_telepon_pendamping
        }

    def get_info_task(self, obj):
        data = []
        queryset = HackathonTask.objects.filter(
            track=obj.track).order_by('order')

        list_qs = list(queryset.values())

        json_list_all = json.loads("[]")

        for e in queryset:

            json_list = json.loads(
                '{"task" : [], "response": []}'
            )

            qs_response = TaskResponse.objects.filter(team=obj, task=e).first()

            if qs_response:

                json_list["task"] = json.loads(
                    json.dumps(HackathonTaskSerializer(e).data)
                )

                json_list["response"] = json.loads(
                    json.dumps(TaskResponseSerializer(qs_response).data)
                )

            else:
                json_list["task"] = json.loads(
                    json.dumps(HackathonTaskSerializer(e).data)
                )

            json_list_all.append(json_list)

        return json_list_all


class TeamMemberSerializer(serializers.ModelSerializer):
    """
        Serializer untuk data model TeamMember
    """

    class Meta:
        model = TeamMember
        fields = (
            'id', 'nama_lengkap', 'email', 'nomor_identitas', 'tanggal_lahir',
            'vegetarian_bool', 'alergi_makanan', 'id_line' 'nomor_telepon'
        )


class AddAnggotaSerializer(serializers.Serializer):
    team_id = serializers.IntegerField()
    full_name = serializers.CharField()
    email = serializers.EmailField()
    id_line = serializers.CharField(required=False, allow_blank=True)
    nomor_telepon = serializers.CharField()
    nomor_id = serializers.CharField()
    tanggal_lahir = serializers.DateField()
    alamat = serializers.CharField()

    class Meta:
        model = TeamMember
        fields = (
            'nama_lengkap', 'email', 'nomor_identitas', 'tanggal_lahir',
            'id_line' 'nomor_telepon', 'alamat'
        )


class UserSerializer(serializers.Serializer):
    full_name = serializers.CharField()
    email = serializers.EmailField()
    id_line = serializers.CharField()
    nomor_telepon = serializers.CharField()
    nomor_id = serializers.CharField()
    tanggal_lahir = serializers.DateField()
    alamat = serializers.CharField()