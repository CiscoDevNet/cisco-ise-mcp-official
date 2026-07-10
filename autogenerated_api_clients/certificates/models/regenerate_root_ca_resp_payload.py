from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.regenerate_root_ca_response import RegenerateRootCaResponse





T = TypeVar("T", bound="RegenerateRootCaRespPayload")



@_attrs_define
class RegenerateRootCaRespPayload:
    

    response: Union[Unset, 'RegenerateRootCaResponse'] = UNSET
    version: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.regenerate_root_ca_response import RegenerateRootCaResponse
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
        from ..models.regenerate_root_ca_response import RegenerateRootCaResponse
        d = dict(src_dict)
        _response = d.pop("response", UNSET)
        response: Union[Unset, RegenerateRootCaResponse]
        if isinstance(_response,  Unset):
            response = UNSET
        else:
            response = RegenerateRootCaResponse.from_dict(_response)




        version = d.pop("version", UNSET)

        regenerate_root_ca_resp_payload = cls(
            response=response,
            version=version,
        )


        regenerate_root_ca_resp_payload.additional_properties = d
        return regenerate_root_ca_resp_payload

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
