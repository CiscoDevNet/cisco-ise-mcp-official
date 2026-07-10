from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import cast, Union
from typing import Union

if TYPE_CHECKING:
  from ..models.link import Link





T = TypeVar("T", bound="SystemCertificateResponse")



@_attrs_define
class SystemCertificateResponse:
    

    expiration_date: Union[Unset, str] = UNSET
    """ Time and date past which the certificate is no longer valid """
    friendly_name: Union[Unset, str] = UNSET
    """ Friendly name of system certificate """
    group_tag: Union[Unset, str] = UNSET
    id: Union[Unset, str] = UNSET
    """ ID of system certificate """
    issued_by: Union[Unset, str] = UNSET
    """ Common Name of the certificate issuer """
    issued_to: Union[Unset, str] = UNSET
    """ Common Name of the certificate subject """
    key_size: Union[Unset, int] = UNSET
    """ Length of the key used for encrypting system certificate """
    link: Union['Link', None, Unset] = UNSET
    portals_using_the_tag: Union[Unset, str] = UNSET
    self_signed: Union[Unset, bool] = UNSET
    serial_number_decimal_format: Union[Unset, str] = UNSET
    """ Used to uniquely identify the certificate within a CA's systems """
    sha_256_fingerprint: Union[Unset, str] = UNSET
    signature_algorithm: Union[Unset, str] = UNSET
    used_by: Union[Unset, str] = UNSET
    valid_from: Union[Unset, str] = UNSET
    """ Time and date on which the certificate was created, also known as the Not Before certificate attribute """
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.link import Link
        expiration_date = self.expiration_date

        friendly_name = self.friendly_name

        group_tag = self.group_tag

        id = self.id

        issued_by = self.issued_by

        issued_to = self.issued_to

        key_size = self.key_size

        link: Union[None, Unset, dict[str, Any]]
        if isinstance(self.link, Unset):
            link = UNSET
        elif isinstance(self.link, Link):
            link = self.link.to_dict()
        else:
            link = self.link

        portals_using_the_tag = self.portals_using_the_tag

        self_signed = self.self_signed

        serial_number_decimal_format = self.serial_number_decimal_format

        sha_256_fingerprint = self.sha_256_fingerprint

        signature_algorithm = self.signature_algorithm

        used_by = self.used_by

        valid_from = self.valid_from


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if expiration_date is not UNSET:
            field_dict["expirationDate"] = expiration_date
        if friendly_name is not UNSET:
            field_dict["friendlyName"] = friendly_name
        if group_tag is not UNSET:
            field_dict["groupTag"] = group_tag
        if id is not UNSET:
            field_dict["id"] = id
        if issued_by is not UNSET:
            field_dict["issuedBy"] = issued_by
        if issued_to is not UNSET:
            field_dict["issuedTo"] = issued_to
        if key_size is not UNSET:
            field_dict["keySize"] = key_size
        if link is not UNSET:
            field_dict["link"] = link
        if portals_using_the_tag is not UNSET:
            field_dict["portalsUsingTheTag"] = portals_using_the_tag
        if self_signed is not UNSET:
            field_dict["selfSigned"] = self_signed
        if serial_number_decimal_format is not UNSET:
            field_dict["serialNumberDecimalFormat"] = serial_number_decimal_format
        if sha_256_fingerprint is not UNSET:
            field_dict["sha256Fingerprint"] = sha_256_fingerprint
        if signature_algorithm is not UNSET:
            field_dict["signatureAlgorithm"] = signature_algorithm
        if used_by is not UNSET:
            field_dict["usedBy"] = used_by
        if valid_from is not UNSET:
            field_dict["validFrom"] = valid_from

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.link import Link
        d = dict(src_dict)
        expiration_date = d.pop("expirationDate", UNSET)

        friendly_name = d.pop("friendlyName", UNSET)

        group_tag = d.pop("groupTag", UNSET)

        id = d.pop("id", UNSET)

        issued_by = d.pop("issuedBy", UNSET)

        issued_to = d.pop("issuedTo", UNSET)

        key_size = d.pop("keySize", UNSET)

        def _parse_link(data: object) -> Union['Link', None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_link_type_0 = Link.from_dict(data)



                return componentsschemas_link_type_0
            except: # noqa: E722
                pass
            return cast(Union['Link', None, Unset], data)

        link = _parse_link(d.pop("link", UNSET))


        portals_using_the_tag = d.pop("portalsUsingTheTag", UNSET)

        self_signed = d.pop("selfSigned", UNSET)

        serial_number_decimal_format = d.pop("serialNumberDecimalFormat", UNSET)

        sha_256_fingerprint = d.pop("sha256Fingerprint", UNSET)

        signature_algorithm = d.pop("signatureAlgorithm", UNSET)

        used_by = d.pop("usedBy", UNSET)

        valid_from = d.pop("validFrom", UNSET)

        system_certificate_response = cls(
            expiration_date=expiration_date,
            friendly_name=friendly_name,
            group_tag=group_tag,
            id=id,
            issued_by=issued_by,
            issued_to=issued_to,
            key_size=key_size,
            link=link,
            portals_using_the_tag=portals_using_the_tag,
            self_signed=self_signed,
            serial_number_decimal_format=serial_number_decimal_format,
            sha_256_fingerprint=sha_256_fingerprint,
            signature_algorithm=signature_algorithm,
            used_by=used_by,
            valid_from=valid_from,
        )


        system_certificate_response.additional_properties = d
        return system_certificate_response

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
