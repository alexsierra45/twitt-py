# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: follow.proto
# Protobuf Python Version: 5.26.1
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0c\x66ollow.proto\x12\x07twittpy\"<\n\x11\x46ollowUserRequest\x12\x0f\n\x07user_id\x18\x01 \x01(\t\x12\x16\n\x0etarget_user_id\x18\x02 \x01(\t\"\x14\n\x12\x46ollowUserResponse\">\n\x13UnfollowUserRequest\x12\x0f\n\x07user_id\x18\x01 \x01(\t\x12\x16\n\x0etarget_user_id\x18\x02 \x01(\t\"\x16\n\x14UnfollowUserResponse\"&\n\x13GetFollowingRequest\x12\x0f\n\x07user_id\x18\x01 \x01(\t\"3\n\x14GetFollowingResponse\x12\x1b\n\x13\x66ollowing_usernames\x18\x01 \x03(\t2\xf0\x01\n\rFollowService\x12\x45\n\nFollowUser\x12\x1a.twittpy.FollowUserRequest\x1a\x1b.twittpy.FollowUserResponse\x12K\n\x0cUnfollowUser\x12\x1c.twittpy.UnfollowUserRequest\x1a\x1d.twittpy.UnfollowUserResponse\x12K\n\x0cGetFollowing\x12\x1c.twittpy.GetFollowingRequest\x1a\x1d.twittpy.GetFollowingResponseb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'follow_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_FOLLOWUSERREQUEST']._serialized_start=25
  _globals['_FOLLOWUSERREQUEST']._serialized_end=85
  _globals['_FOLLOWUSERRESPONSE']._serialized_start=87
  _globals['_FOLLOWUSERRESPONSE']._serialized_end=107
  _globals['_UNFOLLOWUSERREQUEST']._serialized_start=109
  _globals['_UNFOLLOWUSERREQUEST']._serialized_end=171
  _globals['_UNFOLLOWUSERRESPONSE']._serialized_start=173
  _globals['_UNFOLLOWUSERRESPONSE']._serialized_end=195
  _globals['_GETFOLLOWINGREQUEST']._serialized_start=197
  _globals['_GETFOLLOWINGREQUEST']._serialized_end=235
  _globals['_GETFOLLOWINGRESPONSE']._serialized_start=237
  _globals['_GETFOLLOWINGRESPONSE']._serialized_end=288
  _globals['_FOLLOWSERVICE']._serialized_start=291
  _globals['_FOLLOWSERVICE']._serialized_end=531
# @@protoc_insertion_point(module_scope)
