# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: posts_service.proto
# Protobuf Python Version: 5.26.1
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from proto import models_pb2 as models__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x13posts_service.proto\x12\x07twittpy\x1a\x0cmodels.proto\"5\n\x11\x43reatePostRequest\x12\x0f\n\x07user_id\x18\x01 \x01(\t\x12\x0f\n\x07\x63ontent\x18\x02 \x01(\t\"1\n\x12\x43reatePostResponse\x12\x1b\n\x04post\x18\x01 \x01(\x0b\x32\r.twittpy.Post\"!\n\x0eGetPostRequest\x12\x0f\n\x07post_id\x18\x01 \x01(\t\".\n\x0fGetPostResponse\x12\x1b\n\x04post\x18\x01 \x01(\x0b\x32\r.twittpy.Post\"K\n\rRepostRequest\x12\x0f\n\x07user_id\x18\x01 \x01(\t\x12\x18\n\x10original_post_id\x18\x02 \x01(\t\x12\x0f\n\x07\x63ontent\x18\x03 \x01(\t\"-\n\x0eRepostResponse\x12\x1b\n\x04post\x18\x01 \x01(\x0b\x32\r.twittpy.Post\"&\n\x13GetUserPostsRequest\x12\x0f\n\x07user_id\x18\x01 \x01(\t\"4\n\x14GetUserPostsResponse\x12\x1c\n\x05posts\x18\x01 \x03(\x0b\x32\r.twittpy.Post\"$\n\x11\x44\x65letePostRequest\x12\x0f\n\x07post_id\x18\x01 \x01(\t\"\x14\n\x12\x44\x65letePostResponse2\xe1\x02\n\x0bPostService\x12\x45\n\nCreatePost\x12\x1a.twittpy.CreatePostRequest\x1a\x1b.twittpy.CreatePostResponse\x12<\n\x07GetPost\x12\x17.twittpy.GetPostRequest\x1a\x18.twittpy.GetPostResponse\x12\x39\n\x06Repost\x12\x16.twittpy.RepostRequest\x1a\x17.twittpy.RepostResponse\x12\x45\n\nDeletePost\x12\x1a.twittpy.DeletePostRequest\x1a\x1b.twittpy.DeletePostResponse\x12K\n\x0cGetUserPosts\x12\x1c.twittpy.GetUserPostsRequest\x1a\x1d.twittpy.GetUserPostsResponseb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'posts_service_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_CREATEPOSTREQUEST']._serialized_start=46
  _globals['_CREATEPOSTREQUEST']._serialized_end=99
  _globals['_CREATEPOSTRESPONSE']._serialized_start=101
  _globals['_CREATEPOSTRESPONSE']._serialized_end=150
  _globals['_GETPOSTREQUEST']._serialized_start=152
  _globals['_GETPOSTREQUEST']._serialized_end=185
  _globals['_GETPOSTRESPONSE']._serialized_start=187
  _globals['_GETPOSTRESPONSE']._serialized_end=233
  _globals['_REPOSTREQUEST']._serialized_start=235
  _globals['_REPOSTREQUEST']._serialized_end=310
  _globals['_REPOSTRESPONSE']._serialized_start=312
  _globals['_REPOSTRESPONSE']._serialized_end=357
  _globals['_GETUSERPOSTSREQUEST']._serialized_start=359
  _globals['_GETUSERPOSTSREQUEST']._serialized_end=397
  _globals['_GETUSERPOSTSRESPONSE']._serialized_start=399
  _globals['_GETUSERPOSTSRESPONSE']._serialized_end=451
  _globals['_DELETEPOSTREQUEST']._serialized_start=453
  _globals['_DELETEPOSTREQUEST']._serialized_end=489
  _globals['_DELETEPOSTRESPONSE']._serialized_start=491
  _globals['_DELETEPOSTRESPONSE']._serialized_end=511
  _globals['_POSTSERVICE']._serialized_start=514
  _globals['_POSTSERVICE']._serialized_end=867
# @@protoc_insertion_point(module_scope)
