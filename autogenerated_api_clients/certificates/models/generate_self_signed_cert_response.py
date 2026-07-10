from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import Union






T = TypeVar("T", bound="GenerateSelfSignedCertResponse")



@_attrs_define
class GenerateSelfSignedCertResponse:
    

    id: Union[Unset, str] = UNSET
    """ ID of the generated self-signed system certificate """
    message: Union[Unset, str] = UNSET
    """ Response message on generation of self-signed system certificate """
    status: Union[Unset, str] = UNSET
    """ HTTP response status after import """
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        id = self.id

        message = self.message

        status = self.status


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if id is not UNSET:
            field_dict["id"] = id
        if message is not UNSET:
            field_dict["message"] = message
        if status is not UNSET:
            field_dict["status"] = status

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id", UNSET)

        message = d.pop("message", UNSET)

        status = d.pop("status", UNSET)

        generate_self_signed_cert_response = cls(
            id=id,
            message=message,
            status=status,
        )


        generate_self_signed_cert_response.additional_properties = d
        return generate_self_signed_cert_response

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
