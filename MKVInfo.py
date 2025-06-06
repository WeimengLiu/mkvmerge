# To use this code, make sure you
#
#     import json
#
# and then, to convert JSON from a string, do
#
#     result = MkvInfo_from_dict(json.loads(json_string))

from typing import Any, Optional, List, TypeVar, Type, cast, Callable


T = TypeVar("T")


def from_int(x: Any) -> int:
    if x is None:
        return None
    assert isinstance(x, int) and not isinstance(x, bool)
    return x


def from_str(x: Any) -> str:
    if x is None:
        return None
    assert isinstance(x, str)
    return x


def from_none(x: Any) -> Any:
    assert x is None
    return x


def from_union(fs, x):
    for f in fs:
        try:
            return f(x)
        except:
            pass
    assert False


def to_class(c: Type[T], x: Any) -> dict:
    if x is None:
        return None
    assert isinstance(x, c)
    return cast(Any, x).to_dict()


def from_list(f: Callable[[Any], T], x: Any) -> List[T]:
    if x is None:
        return None
    assert isinstance(x, list)
    return [f(y) for y in x]


def from_bool(x: Any) -> bool:
    if x is None:
        return None
    assert isinstance(x, bool)
    return x


def from_float(x: Any) -> float:
    if x is None:
        return None
    assert isinstance(x, (float, int)) and not isinstance(x, bool)
    return float(x)


def to_float(x: Any) -> float:
    if x is None:
        return None
    assert isinstance(x, float)
    return x


class AttachmentProperties:
    uid: int

    def __init__(self, uid: int) -> None:
        self.uid = uid

    @staticmethod
    def from_dict(obj: Any) -> 'AttachmentProperties':
        assert isinstance(obj, dict)
        uid = from_int(obj.get("uid"))
        return AttachmentProperties(uid)

    def to_dict(self) -> dict:
        result: dict = {}
        result["uid"] = from_int(self.uid)
        return result


class Attachment:
    file_name: str
    id: int
    properties: Optional[AttachmentProperties]
    size: int
    type: Optional[str]
    description: Optional[str]
    content_type: str

    def __init__(self, file_name: str, id: int, properties: AttachmentProperties, size: int, type: Optional[str], description: Optional[str], content_type: str) -> None:
        self.file_name = file_name
        self.id = id
        self.properties = properties
        self.size = size
        self.type = type
        self.description = description
        self.content_type = content_type

    @staticmethod
    def from_dict(obj: Any) -> 'Attachment':
        assert isinstance(obj, dict)
        file_name = from_str(obj.get("file_name"))
        id = from_int(obj.get("id"))
        properties = AttachmentProperties.from_dict(obj.get("properties"))
        size = from_int(obj.get("size"))
        type = from_union([from_str, from_none], obj.get("type"))
        description = from_union([from_str, from_none], obj.get("description"))
        content_type = from_str(obj.get("content_type"))
        return Attachment(file_name, id, properties, size, type, description, content_type)

    def to_dict(self) -> dict:
        result: dict = {}
        result["file_name"] = from_str(self.file_name)
        result["id"] = from_int(self.id)
        result["properties"] = to_class(AttachmentProperties, self.properties)
        result["size"] = from_int(self.size)
        if self.type is not None:
            result["type"] = from_union([from_str, from_none], self.type)
        if self.description is not None:
            result["description"] = from_union([from_str, from_none], self.description)
        result["content_type"] = from_str(self.content_type)
        return result


class Chapter:
    num_entries: int

    def __init__(self, num_entries: int) -> None:
        self.num_entries = num_entries

    @staticmethod
    def from_dict(obj: Any) -> 'Chapter':
        assert isinstance(obj, dict)
        num_entries = from_int(obj.get("num_entries"))
        return Chapter(num_entries)

    def to_dict(self) -> dict:
        result: dict = {}
        result["num_entries"] = from_int(self.num_entries)
        return result


class Program:
    service_name: Optional[str]
    program_number: Optional[int]
    service_provider: Optional[str]

    def __init__(self, service_name: Optional[str], program_number: Optional[int], service_provider: Optional[str]) -> None:
        self.service_name = service_name
        self.program_number = program_number
        self.service_provider = service_provider

    @staticmethod
    def from_dict(obj: Any) -> 'Program':
        assert isinstance(obj, dict)
        service_name = from_union([from_str, from_none], obj.get("service_name"))
        program_number = from_union([from_int, from_none], obj.get("program_number"))
        service_provider = from_union([from_str, from_none], obj.get("service_provider"))
        return Program(service_name, program_number, service_provider)

    def to_dict(self) -> dict:
        result: dict = {}
        if self.service_name is not None:
            result["service_name"] = from_union([from_str, from_none], self.service_name)
        if self.program_number is not None:
            result["program_number"] = from_union([from_int, from_none], self.program_number)
        if self.service_provider is not None:
            result["service_provider"] = from_union([from_str, from_none], self.service_provider)
        return result


class ContainerProperties:
    previous_segment_uid: str
    container_type: int
    date_local: str
    playlist_chapters: int
    programs: List[Program]
    duration: int
    next_segment_uid: str
    other_file: List[str]
    title: str
    segment_uid: str
    playlist: bool
    writing_application: str
    date_utc: str
    is_providing_timestamps: bool

    def __init__(self, previous_segment_uid: str, container_type: int, date_local: str, playlist_chapters: int, programs: List[Program], duration: int, next_segment_uid: str, other_file: List[str], title: str, segment_uid: str, playlist: bool, writing_application: str, date_utc: str, is_providing_timestamps: bool) -> None:
        self.previous_segment_uid = previous_segment_uid
        self.container_type = container_type
        self.date_local = date_local
        self.playlist_chapters = playlist_chapters
        self.programs = programs
        self.duration = duration
        self.next_segment_uid = next_segment_uid
        self.other_file = other_file
        self.title = title
        self.segment_uid = segment_uid
        self.playlist = playlist
        self.writing_application = writing_application
        self.date_utc = date_utc
        self.is_providing_timestamps = is_providing_timestamps

    @staticmethod
    def from_dict(obj: Any) -> 'ContainerProperties':
        assert isinstance(obj, dict)
        previous_segment_uid = from_str(obj.get("previous_segment_uid"))
        container_type = from_int(obj.get("container_type"))
        date_local = from_str(obj.get("date_local"))
        playlist_chapters = from_int(obj.get("playlist_chapters"))
        programs = from_list(Program.from_dict, obj.get("programs"))
        duration = from_int(obj.get("duration"))
        next_segment_uid = from_str(obj.get("next_segment_uid"))
        other_file = from_list(from_str, obj.get("other_file"))
        title = from_str(obj.get("title"))
        segment_uid = from_str(obj.get("segment_uid"))
        playlist = from_bool(obj.get("playlist"))
        writing_application = from_str(obj.get("writing_application"))
        date_utc = from_str(obj.get("date_utc"))
        is_providing_timestamps = from_bool(obj.get("is_providing_timestamps"))
        return ContainerProperties(previous_segment_uid, container_type, date_local, playlist_chapters, programs, duration, next_segment_uid, other_file, title, segment_uid, playlist, writing_application, date_utc, is_providing_timestamps)

    def to_dict(self) -> dict:
        result: dict = {}
        result["previous_segment_uid"] = from_str(self.previous_segment_uid)
        result["container_type"] = from_int(self.container_type)
        result["date_local"] = from_str(self.date_local)
        result["playlist_chapters"] = from_int(self.playlist_chapters)
        result["programs"] = from_list(lambda x: to_class(Program, x), self.programs)
        result["duration"] = from_int(self.duration)
        result["next_segment_uid"] = from_str(self.next_segment_uid)
        result["other_file"] = from_list(from_str, self.other_file)
        result["title"] = from_str(self.title)
        result["segment_uid"] = from_str(self.segment_uid)
        result["playlist"] = from_bool(self.playlist)
        result["writing_application"] = from_str(self.writing_application)
        result["date_utc"] = from_str(self.date_utc)
        result["is_providing_timestamps"] = from_bool(self.is_providing_timestamps)
        return result


class Container:
    recognized: bool
    supported: bool
    properties: ContainerProperties

    def __init__(self, recognized: bool, supported: bool, properties: ContainerProperties) -> None:
        self.recognized = recognized
        self.supported = supported
        self.properties = properties

    @staticmethod
    def from_dict(obj: Any) -> 'Container':
        assert isinstance(obj, dict)
        recognized = from_bool(obj.get("recognized"))
        supported = from_bool(obj.get("supported"))
        properties = ContainerProperties.from_dict(obj.get("properties"))
        return Container(recognized, supported, properties)

    def to_dict(self) -> dict:
        result: dict = {}
        result["recognized"] = from_bool(self.recognized)
        result["supported"] = from_bool(self.supported)
        result["properties"] = to_class(ContainerProperties, self.properties)
        return result


class TrackTag:
    num_entries: int
    track_id: int

    def __init__(self, num_entries: int, track_id: int) -> None:
        self.num_entries = num_entries
        self.track_id = track_id

    @staticmethod
    def from_dict(obj: Any) -> 'TrackTag':
        assert isinstance(obj, dict)
        num_entries = from_int(obj.get("num_entries"))
        track_id = from_int(obj.get("track_id"))
        return TrackTag(num_entries, track_id)

    def to_dict(self) -> dict:
        result: dict = {}
        result["num_entries"] = from_int(self.num_entries)
        result["track_id"] = from_int(self.track_id)
        return result


class TrackProperties:
    color_matrix_coefficients: Optional[int]
    default_duration: Optional[int]
    codec_delay: Optional[int]
    flag_original: Optional[bool]
    number: Optional[int]
    codec_private_length: Optional[int]
    uid: Optional[int]
    track_name: Optional[str]
    encoding: Optional[str]
    tag_title: Optional[str]
    teletext_page: Optional[int]
    stream_id: Optional[int]
    packetizer: Optional[str]
    flag_hearing_impaired: bool
    color_primaries: Optional[int]
    audio_bits_per_sample: Optional[int]
    content_encoding_algorithms: Optional[str]
    max_frame_light: Optional[int]
    projection_pose_roll: Optional[float]
    flag_text_descriptions: bool
    tag_artist: Optional[str]
    chroma_siting: Optional[str]
    cb_subsample: Optional[str]
    color_range: Optional[int]
    display_dimensions: Optional[str]
    flag_commentary: bool
    tag_fps: Optional[str]
    aac_is_sbr: Optional[str]
    stereo_mode: Optional[int]
    forced_track: Optional[bool]
    min_luminance: Optional[float]
    enabled_track: Optional[bool]
    codec_private_data: Optional[str]
    program_number: Optional[int]
    tag_bitsps: Optional[str]
    audio_channels: Optional[int]
    audio_emphasis: Optional[int]
    audio_sampling_frequency: Optional[int]
    chroma_subsample: Optional[str]
    chromaticity_coordinates: Optional[str]
    codec_id: Optional[str]
    projection_type: Optional[int]
    projection_pose_yaw: Optional[float]
    color_bits_per_channel: Optional[int]
    max_luminance: Optional[float]
    num_index_entries: Optional[int]
    flag_visual_impaired: Optional[bool]
    codec_name: Optional[str]
    white_color_coordinates: Optional[str]
    language: Optional[str]
    sub_stream_id: Optional[int]
    multiplexed_tracks: Optional[List[int]]
    default_track: Optional[bool]
    language_ietf: Optional[str]
    tag_bps: Optional[str]
    projection_pose_pitch: Optional[float]
    minimum_timestamp: Optional[int]
    max_content_light: Optional[int]
    projection_private: Optional[str]
    display_unit: Optional[int]
    color_transfer_characteristics: Optional[int]
    pixel_dimensions: Optional[str]
    text_subtitles: Optional[bool]

    def __init__(self, color_matrix_coefficients: Optional[int], default_duration: Optional[int], codec_delay: Optional[int], flag_original: Optional[bool], number: Optional[int], codec_private_length: Optional[int], uid: Optional[int], track_name: Optional[str], encoding: Optional[str], tag_title: Optional[str], teletext_page: Optional[int], stream_id: Optional[int], packetizer: Optional[str], flag_hearing_impaired: bool, color_primaries: Optional[int], audio_bits_per_sample: Optional[int], content_encoding_algorithms: Optional[str], max_frame_light: int, projection_pose_roll: Optional[float], flag_text_descriptions: Optional[bool], tag_artist: Optional[str], chroma_siting: Optional[str], cb_subsample: Optional[str], color_range: int, display_dimensions: Optional[str], flag_commentary: bool, tag_fps: Optional[str], aac_is_sbr: Optional[str], stereo_mode: Optional[int], forced_track: Optional[bool], min_luminance: Optional[float], enabled_track: Optional[bool], codec_private_data: Optional[str], program_number: Optional[int], tag_bitsps: Optional[str], audio_channels: Optional[int], audio_emphasis: Optional[int], audio_sampling_frequency: Optional[int], chroma_subsample: Optional[str], chromaticity_coordinates: Optional[str], codec_id: Optional[str], projection_type: Optional[int], projection_pose_yaw: Optional[float], color_bits_per_channel: Optional[int], max_luminance: Optional[float], num_index_entries: Optional[int], flag_visual_impaired: Optional[bool], codec_name: Optional[str], white_color_coordinates: Optional[str], language: Optional[str], sub_stream_id: Optional[int], multiplexed_tracks: Optional[List[int]], default_track: Optional[bool], language_ietf: Optional[str], tag_bps: Optional[str], projection_pose_pitch: Optional[float], minimum_timestamp: Optional[int], max_content_light: Optional[int], projection_private: Optional[str], display_unit: Optional[int], color_transfer_characteristics: Optional[int], pixel_dimensions: Optional[str], text_subtitles: Optional[bool]) -> None:
        self.color_matrix_coefficients = color_matrix_coefficients
        self.default_duration = default_duration
        self.codec_delay = codec_delay
        self.flag_original = flag_original
        self.number = number
        self.codec_private_length = codec_private_length
        self.uid = uid
        self.track_name = track_name
        self.encoding = encoding
        self.tag_title = tag_title
        self.teletext_page = teletext_page
        self.stream_id = stream_id
        self.packetizer = packetizer
        self.flag_hearing_impaired = flag_hearing_impaired
        self.color_primaries = color_primaries
        self.audio_bits_per_sample = audio_bits_per_sample
        self.content_encoding_algorithms = content_encoding_algorithms
        self.max_frame_light = max_frame_light
        self.projection_pose_roll = projection_pose_roll
        self.flag_text_descriptions = flag_text_descriptions
        self.tag_artist = tag_artist
        self.chroma_siting = chroma_siting
        self.cb_subsample = cb_subsample
        self.color_range = color_range
        self.display_dimensions = display_dimensions
        self.flag_commentary = flag_commentary
        self.tag_fps = tag_fps
        self.aac_is_sbr = aac_is_sbr
        self.stereo_mode = stereo_mode
        self.forced_track = forced_track
        self.min_luminance = min_luminance
        self.enabled_track = enabled_track
        self.codec_private_data = codec_private_data
        self.program_number = program_number
        self.tag_bitsps = tag_bitsps
        self.audio_channels = audio_channels
        self.audio_emphasis = audio_emphasis
        self.audio_sampling_frequency = audio_sampling_frequency
        self.chroma_subsample = chroma_subsample
        self.chromaticity_coordinates = chromaticity_coordinates
        self.codec_id = codec_id
        self.projection_type = projection_type
        self.projection_pose_yaw = projection_pose_yaw
        self.color_bits_per_channel = color_bits_per_channel
        self.max_luminance = max_luminance
        self.num_index_entries = num_index_entries
        self.flag_visual_impaired = flag_visual_impaired
        self.codec_name = codec_name
        self.white_color_coordinates = white_color_coordinates
        self.language = language
        self.sub_stream_id = sub_stream_id
        self.multiplexed_tracks = multiplexed_tracks
        self.default_track = default_track
        self.language_ietf = language_ietf
        self.tag_bps = tag_bps
        self.projection_pose_pitch = projection_pose_pitch
        self.minimum_timestamp = minimum_timestamp
        self.max_content_light = max_content_light
        self.projection_private = projection_private
        self.display_unit = display_unit
        self.color_transfer_characteristics = color_transfer_characteristics
        self.pixel_dimensions = pixel_dimensions
        self.text_subtitles = text_subtitles

    @staticmethod
    def from_dict(obj: Any) -> 'TrackProperties':
        assert isinstance(obj, dict)
        color_matrix_coefficients = from_union([from_int, from_none], obj.get("color_matrix_coefficients"))
        default_duration = from_union([from_int, from_none], obj.get("default_duration"))
        codec_delay = from_int(obj.get("codec_delay"))
        flag_original = from_bool(obj.get("flag_original"))
        number = from_int(obj.get("number"))
        codec_private_length = from_int(obj.get("codec_private_length"))
        uid = from_union([from_int, from_none], obj.get("uid"))
        track_name = from_str(obj.get("track_name"))
        encoding = from_str(obj.get("encoding"))
        tag_title = from_union([from_str, from_none], obj.get("tag_title"))
        teletext_page = from_int(obj.get("teletext_page"))
        stream_id = from_union([from_int, from_none], obj.get("stream_id"))
        packetizer = from_str(obj.get("packetizer"))
        flag_hearing_impaired = from_bool(obj.get("flag_hearing_impaired"))
        color_primaries = from_union([from_int, from_none], obj.get("color_primaries"))
        audio_bits_per_sample = from_union([from_int, from_none], obj.get("audio_bits_per_sample"))
        content_encoding_algorithms = from_str(obj.get("content_encoding_algorithms"))
        max_frame_light = from_int(obj.get("max_frame_light"))
        projection_pose_roll = from_union([from_float, from_none], obj.get("projection_pose_roll"))
        flag_text_descriptions = from_bool(obj.get("flag_text_descriptions"))
        tag_artist = from_union([from_str, from_none], obj.get("tag_artist"))
        chroma_siting = from_str(obj.get("chroma_siting"))
        cb_subsample = from_str(obj.get("cb_subsample"))
        color_range = from_int(obj.get("color_range"))
        display_dimensions = from_union([from_str, from_none], obj.get("display_dimensions"))
        flag_commentary = from_bool(obj.get("flag_commentary"))
        tag_fps = from_union([from_str, from_none], obj.get("tag_fps"))
        aac_is_sbr = from_str(obj.get("aac_is_sbr"))
        stereo_mode = from_union([from_int, from_none], obj.get("stereo_mode"))
        forced_track = from_union([from_bool, from_none], obj.get("forced_track"))
        min_luminance = from_union([from_float, from_none], obj.get("min_luminance"))
        enabled_track = from_union([from_bool, from_none], obj.get("enabled_track"))
        codec_private_data = from_str(obj.get("codec_private_data"))
        program_number = from_int(obj.get("program_number"))
        tag_bitsps = from_str(obj.get("tag_bitsps"))
        audio_channels = from_int(obj.get("audio_channels"))
        audio_emphasis = from_union([from_int, from_none], obj.get("audio_emphasis"))
        audio_sampling_frequency = from_int(obj.get("audio_sampling_frequency"))
        chroma_subsample = from_union([from_str, from_none], obj.get("chroma_subsample"))
        chromaticity_coordinates = from_union([from_str, from_none], obj.get("chromaticity_coordinates"))
        codec_id = from_union([from_str, from_none], obj.get("codec_id"))
        projection_type = from_union([from_int, from_none], obj.get("projection_type"))
        projection_pose_yaw = from_union([from_float, from_none], obj.get("projection_pose_yaw"))
        color_bits_per_channel = from_union([from_int, from_none], obj.get("color_bits_per_channel"))
        max_luminance = from_union([from_float, from_none], obj.get("max_luminance"))
        num_index_entries = from_union([from_int, from_none], obj.get("num_index_entries"))
        flag_visual_impaired = from_union([from_bool, from_none], obj.get("flag_visual_impaired"))
        codec_name = from_union([from_str, from_none], obj.get("codec_name"))
        white_color_coordinates = from_union([from_str, from_none], obj.get("white_color_coordinates"))
        language = from_union([from_str, from_none], obj.get("language"))
        sub_stream_id = from_union([from_int, from_none], obj.get("sub_stream_id"))
        multiplexed_tracks = from_union([lambda x: from_list(from_int, x), from_none], obj.get("multiplexed_tracks"))
        default_track = from_union([from_bool, from_none], obj.get("default_track"))
        language_ietf = from_union([from_str, from_none], obj.get("language_ietf"))
        tag_bps = from_union([from_str, from_none], obj.get("tag_bps"))
        projection_pose_pitch = from_union([from_float, from_none], obj.get("projection_pose_pitch"))
        minimum_timestamp = from_union([from_int, from_none], obj.get("minimum_timestamp"))
        max_content_light = from_union([from_int, from_none], obj.get("max_content_light"))
        projection_private = from_union([from_str, from_none], obj.get("projection_private"))
        display_unit = from_union([from_int, from_none], obj.get("display_unit"))
        color_transfer_characteristics = from_union([from_int, from_none], obj.get("color_transfer_characteristics"))
        pixel_dimensions = from_union([from_str, from_none], obj.get("pixel_dimensions"))
        text_subtitles = from_union([from_bool, from_none], obj.get("text_subtitles"))
        return TrackProperties(color_matrix_coefficients, default_duration, codec_delay, flag_original, number, codec_private_length, uid, track_name, encoding, tag_title, teletext_page, stream_id, packetizer, flag_hearing_impaired, color_primaries, audio_bits_per_sample, content_encoding_algorithms, max_frame_light, projection_pose_roll, flag_text_descriptions, tag_artist, chroma_siting, cb_subsample, color_range, display_dimensions, flag_commentary, tag_fps, aac_is_sbr, stereo_mode, forced_track, min_luminance, enabled_track, codec_private_data, program_number, tag_bitsps, audio_channels, audio_emphasis, audio_sampling_frequency, chroma_subsample, chromaticity_coordinates, codec_id, projection_type, projection_pose_yaw, color_bits_per_channel, max_luminance, num_index_entries, flag_visual_impaired, codec_name, white_color_coordinates, language, sub_stream_id, multiplexed_tracks, default_track, language_ietf, tag_bps, projection_pose_pitch, minimum_timestamp, max_content_light, projection_private, display_unit, color_transfer_characteristics, pixel_dimensions, text_subtitles)

    def to_dict(self) -> dict:
        result: dict = {}
        if self.color_matrix_coefficients is not None:
            result["color_matrix_coefficients"] = from_union([from_int, from_none], self.color_matrix_coefficients)
        if self.default_duration is not None:
            result["default_duration"] = from_union([from_int, from_none], self.default_duration)
        result["codec_delay"] = from_int(self.codec_delay)
        result["flag_original"] = from_bool(self.flag_original)
        result["number"] = from_int(self.number)
        result["codec_private_length"] = from_int(self.codec_private_length)
        if self.uid is not None:
            result["uid"] = from_union([from_int, from_none], self.uid)
        result["track_name"] = from_str(self.track_name)
        result["encoding"] = from_str(self.encoding)
        if self.tag_title is not None:
            result["tag_title"] = from_union([from_str, from_none], self.tag_title)
        result["teletext_page"] = from_int(self.teletext_page)
        if self.stream_id is not None:
            result["stream_id"] = from_union([from_int, from_none], self.stream_id)
        result["packetizer"] = from_str(self.packetizer)
        result["flag_hearing_impaired"] = from_bool(self.flag_hearing_impaired)
        if self.color_primaries is not None:
            result["color_primaries"] = from_union([from_int, from_none], self.color_primaries)
        if self.audio_bits_per_sample is not None:
            result["audio_bits_per_sample"] = from_union([from_int, from_none], self.audio_bits_per_sample)
        result["content_encoding_algorithms"] = from_str(self.content_encoding_algorithms)
        result["max_frame_light"] = from_int(self.max_frame_light)
        if self.projection_pose_roll is not None:
            result["projection_pose_roll"] = from_union([to_float, from_none], self.projection_pose_roll)
        result["flag_text_descriptions"] = from_bool(self.flag_text_descriptions)
        if self.tag_artist is not None:
            result["tag_artist"] = from_union([from_str, from_none], self.tag_artist)
        result["chroma_siting"] = from_str(self.chroma_siting)
        result["cb_subsample"] = from_str(self.cb_subsample)
        result["color_range"] = from_int(self.color_range)
        if self.display_dimensions is not None:
            result["display_dimensions"] = from_union([from_str, from_none], self.display_dimensions)
        result["flag_commentary"] = from_bool(self.flag_commentary)
        if self.tag_fps is not None:
            result["tag_fps"] = from_union([from_str, from_none], self.tag_fps)
        result["aac_is_sbr"] = from_str(self.aac_is_sbr)
        if self.stereo_mode is not None:
            result["stereo_mode"] = from_union([from_int, from_none], self.stereo_mode)
        if self.forced_track is not None:
            result["forced_track"] = from_union([from_bool, from_none], self.forced_track)
        if self.min_luminance is not None:
            result["min_luminance"] = from_union([to_float, from_none], self.min_luminance)
        if self.enabled_track is not None:
            result["enabled_track"] = from_union([from_bool, from_none], self.enabled_track)
        result["codec_private_data"] = from_str(self.codec_private_data)
        result["program_number"] = from_int(self.program_number)
        result["tag_bitsps"] = from_str(self.tag_bitsps)
        result["audio_channels"] = from_int(self.audio_channels)
        if self.audio_emphasis is not None:
            result["audio_emphasis"] = from_union([from_int, from_none], self.audio_emphasis)
        result["audio_sampling_frequency"] = from_int(self.audio_sampling_frequency)
        if self.chroma_subsample is not None:
            result["chroma_subsample"] = from_union([from_str, from_none], self.chroma_subsample)
        if self.chromaticity_coordinates is not None:
            result["chromaticity_coordinates"] = from_union([from_str, from_none], self.chromaticity_coordinates)
        if self.codec_id is not None:
            result["codec_id"] = from_union([from_str, from_none], self.codec_id)
        if self.projection_type is not None:
            result["projection_type"] = from_union([from_int, from_none], self.projection_type)
        if self.projection_pose_yaw is not None:
            result["projection_pose_yaw"] = from_union([to_float, from_none], self.projection_pose_yaw)
        if self.color_bits_per_channel is not None:
            result["color_bits_per_channel"] = from_union([from_int, from_none], self.color_bits_per_channel)
        if self.max_luminance is not None:
            result["max_luminance"] = from_union([to_float, from_none], self.max_luminance)
        if self.num_index_entries is not None:
            result["num_index_entries"] = from_union([from_int, from_none], self.num_index_entries)
        if self.flag_visual_impaired is not None:
            result["flag_visual_impaired"] = from_union([from_bool, from_none], self.flag_visual_impaired)
        if self.codec_name is not None:
            result["codec_name"] = from_union([from_str, from_none], self.codec_name)
        if self.white_color_coordinates is not None:
            result["white_color_coordinates"] = from_union([from_str, from_none], self.white_color_coordinates)
        if self.language is not None:
            result["language"] = from_union([from_str, from_none], self.language)
        if self.sub_stream_id is not None:
            result["sub_stream_id"] = from_union([from_int, from_none], self.sub_stream_id)
        if self.multiplexed_tracks is not None:
            result["multiplexed_tracks"] = from_union([lambda x: from_list(from_int, x), from_none], self.multiplexed_tracks)
        if self.default_track is not None:
            result["default_track"] = from_union([from_bool, from_none], self.default_track)
        if self.language_ietf is not None:
            result["language_ietf"] = from_union([from_str, from_none], self.language_ietf)
        if self.tag_bps is not None:
            result["tag_bps"] = from_union([from_str, from_none], self.tag_bps)
        if self.projection_pose_pitch is not None:
            result["projection_pose_pitch"] = from_union([to_float, from_none], self.projection_pose_pitch)
        if self.minimum_timestamp is not None:
            result["minimum_timestamp"] = from_union([from_int, from_none], self.minimum_timestamp)
        if self.max_content_light is not None:
            result["max_content_light"] = from_union([from_int, from_none], self.max_content_light)
        if self.projection_private is not None:
            result["projection_private"] = from_union([from_str, from_none], self.projection_private)
        if self.display_unit is not None:
            result["display_unit"] = from_union([from_int, from_none], self.display_unit)
        if self.color_transfer_characteristics is not None:
            result["color_transfer_characteristics"] = from_union([from_int, from_none], self.color_transfer_characteristics)
        if self.pixel_dimensions is not None:
            result["pixel_dimensions"] = from_union([from_str, from_none], self.pixel_dimensions)
        if self.text_subtitles is not None:
            result["text_subtitles"] = from_union([from_bool, from_none], self.text_subtitles)
        return result


class Track:
    codec: str
    id: int
    type: str
    properties: Optional[TrackProperties]
    file_path: Optional[str]


    def __init__(self, codec: str, id: int, type: str, file_path: Optional[str], properties: Optional[TrackProperties]) -> None:
        self.codec = codec
        self.id = id
        self.type = type
        self.properties = properties
        self.file_path = file_path

    @staticmethod
    def from_dict(obj: Any) -> 'Track':
        assert isinstance(obj, dict)
        codec = from_str(obj.get("codec"))
        id = from_int(obj.get("id"))
        type = from_str(obj.get("type"))
        file_path = from_str(obj.get("file_path"))
        properties = from_union([TrackProperties.from_dict, from_none], obj.get("properties"))
        return Track(codec, id, type, file_path ,properties)

    def to_dict(self) -> dict:
        result: dict = {}
        result["codec"] = from_str(self.codec)
        result["id"] = from_int(self.id)
        result["type"] = from_str(self.type)
        result["file_path"] = from_str(self.file_path)
        if self.properties is not None:
            result["properties"] = from_union([lambda x: to_class(TrackProperties, x), from_none], self.properties)
        return result


class MkvInfo:
    errors: List[str]
    container: Container
    global_tags: List[Chapter]
    attachments: List[Attachment]
    chapters: List[Chapter]
    file_name: str
    identification_format_version: int
    track_tags: List[TrackTag]
    tracks: List[Track]


    def __init__(self, errors: List[str], container: Container, global_tags: List[Chapter], attachments: List[Attachment], chapters: List[Chapter], file_name: str, identification_format_version: int, track_tags: List[TrackTag], tracks: List[Track]) -> None:
        self.errors = errors
        self.container = container
        self.global_tags = global_tags
        self.attachments = attachments
        self.chapters = chapters
        self.file_name = file_name
        self.identification_format_version = identification_format_version
        self.track_tags = track_tags
        self.tracks = tracks

    @staticmethod
    def from_dict(obj: Any) -> 'MkvInfo':
        assert isinstance(obj, dict)
        errors = from_list(from_str, obj.get("errors"))
        container = Container.from_dict(obj.get("container"))
        global_tags = from_list(Chapter.from_dict, obj.get("global_tags"))
        attachments = from_list(Attachment.from_dict, obj.get("attachments"))
        chapters = from_list(Chapter.from_dict, obj.get("chapters"))
        file_name = from_str(obj.get("file_name"))
        identification_format_version = from_int(obj.get("identification_format_version"))
        track_tags = from_list(TrackTag.from_dict, obj.get("track_tags"))
        tracks = from_list(Track.from_dict, obj.get("tracks"))
        return MkvInfo(errors, container, global_tags, attachments, chapters, file_name, identification_format_version, track_tags, tracks)

    def to_dict(self) -> dict:
        result: dict = {}
        result["errors"] = from_list(from_str, self.errors)
        result["container"] = to_class(Container, self.container)
        result["global_tags"] = from_list(lambda x: to_class(Chapter, x), self.global_tags)
        result["attachments"] = from_list(lambda x: to_class(Attachment, x), self.attachments)
        result["chapters"] = from_list(lambda x: to_class(Chapter, x), self.chapters)
        result["file_name"] = from_str(self.file_name)
        result["identification_format_version"] = from_int(self.identification_format_version)
        result["track_tags"] = from_list(lambda x: to_class(TrackTag, x), self.track_tags)
        result["tracks"] = from_list(lambda x: to_class(Track, x), self.tracks)
        return result


def mkv_info_from_dict(s: Any) -> MkvInfo:
    return MkvInfo.from_dict(s)


def mkv_info_to_dict(x: MkvInfo) -> Any:
    return to_class(MkvInfo, x)
