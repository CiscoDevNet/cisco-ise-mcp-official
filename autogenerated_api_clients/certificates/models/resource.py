# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import File, FileTypes
from ..types import UNSET, Unset
from io import BytesIO
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.input_stream import InputStream





T = TypeVar("T", bound="Resource")



@_attrs_define
class Resource:
    

    description: Union[Unset, str] = UNSET
    file: Union[Unset, File] = UNSET
    filename: Union[Unset, str] = UNSET
    input_stream: Union[Unset, 'InputStream'] = UNSET
    open_: Union[Unset, bool] = UNSET
    readable: Union[Unset, bool] = UNSET
    uri: Union[Unset, str] = UNSET
    url: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.input_stream import InputStream
        description = self.description

        file: Union[Unset, FileTypes] = UNSET
        if not isinstance(self.file, Unset):
            file = self.file.to_tuple()


        filename = self.filename

        input_stream: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.input_stream, Unset):
            input_stream = self.input_stream.to_dict()

        open_ = self.open_

        readable = self.readable

        uri = self.uri

        url = self.url


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if description is not UNSET:
            field_dict["description"] = description
        if file is not UNSET:
            field_dict["file"] = file
        if filename is not UNSET:
            field_dict["filename"] = filename
        if input_stream is not UNSET:
            field_dict["inputStream"] = input_stream
        if open_ is not UNSET:
            field_dict["open"] = open_
        if readable is not UNSET:
            field_dict["readable"] = readable
        if uri is not UNSET:
            field_dict["uri"] = uri
        if url is not UNSET:
            field_dict["url"] = url

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.input_stream import InputStream
        d = dict(src_dict)
        description = d.pop("description", UNSET)

        _file = d.pop("file", UNSET)
        file: Union[Unset, File]
        if isinstance(_file,  Unset):
            file = UNSET
        else:
            file = File(
             payload = BytesIO(_file)
        )




        filename = d.pop("filename", UNSET)

        _input_stream = d.pop("inputStream", UNSET)
        input_stream: Union[Unset, InputStream]
        if isinstance(_input_stream,  Unset):
            input_stream = UNSET
        else:
            input_stream = InputStream.from_dict(_input_stream)




        open_ = d.pop("open", UNSET)

        readable = d.pop("readable", UNSET)

        uri = d.pop("uri", UNSET)

        url = d.pop("url", UNSET)

        resource = cls(
            description=description,
            file=file,
            filename=filename,
            input_stream=input_stream,
            open_=open_,
            readable=readable,
            uri=uri,
            url=url,
        )


        resource.additional_properties = d
        return resource

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
