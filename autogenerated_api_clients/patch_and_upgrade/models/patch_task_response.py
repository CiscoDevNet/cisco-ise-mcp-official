from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.task_id_response import TaskIdResponse





T = TypeVar("T", bound="PatchTaskResponse")



@_attrs_define
class PatchTaskResponse:
    

    response: Union[Unset, 'TaskIdResponse'] = UNSET
    version: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.task_id_response import TaskIdResponse
        response: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.response, Unset):
            response = self.response.to_dict()

        version = self.version


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if response is not UNSET:
            field_dict["response"] = response
        if version is not UNSET:
            field_dict["version"] = version

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.task_id_response import TaskIdResponse
        d = dict(src_dict)
        _response = d.pop("response", UNSET)
        response: Union[Unset, TaskIdResponse]
        if isinstance(_response,  Unset):
            response = UNSET
        else:
            response = TaskIdResponse.from_dict(_response)




        version = d.pop("version", UNSET)

        patch_task_response = cls(
            response=response,
            version=version,
        )


        patch_task_response.additional_properties = d
        return patch_task_response

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
