from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import Union






T = TypeVar("T", bound="DeleteSystemCertRequest")



@_attrs_define
class DeleteSystemCertRequest:
    

    allow_wildcard_delete: Union[Unset, bool] = UNSET
    """ If the given certificate to be deleted is a wildcard certificate, the corresponding certificate gets deleted
    on the rest of the nodes in the deployment as well. """
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        allow_wildcard_delete = self.allow_wildcard_delete


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if allow_wildcard_delete is not UNSET:
            field_dict["allowWildcardDelete"] = allow_wildcard_delete

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        allow_wildcard_delete = d.pop("allowWildcardDelete", UNSET)

        delete_system_cert_request = cls(
            allow_wildcard_delete=allow_wildcard_delete,
        )


        delete_system_cert_request.additional_properties = d
        return delete_system_cert_request

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
