"""
A framework for declaring memory types and structures in the nintendo switch's
memory space. This allows us to build a map of a program's memory space similar
to making a c-style header file.
"""
from typing import Optional, Iterable, Tuple, Type
from copy import copy
from collections import OrderedDict
from textwrap import indent
from dataclasses import dataclass

from ptai.ppt2.switch import Switch

STRUCT_INDENT = "|     "


class classproperty:
    """
    Decorator that converts a method with a single cls argument into a
    property that can be accessed directly from the class.

    This snippet taken from the Django web framework.
    """
    def __init__(self, method=None):
        self.fget = method

    def __get__(self, instance, cls=None):
        return self.fget(cls)

    def getter(self, method):
        self.fget = method
        return self


class SwitchType:
    """
    Abstract class for switch data types.

    Every type must specify a size which indicates how many bytes of space it
    takes. A types constructor can take any set of parameters, but the
    `from_bytes()` method must be implemented to convert a bytestring of the
    correct size to an instance of the type.
    """

    # Size in bytes of this type.
    # Must be defined statically by concrete classes, either as a normal class
    # attribute or using `classproperty`.
    size:int

    # Class to use instead of `Pointer` as the pointer class when creating the
    # `pointer_t` class attribute.
    pointer_class:Optional["Pointer"] = None

    @classmethod
    def from_bytes(self, data: bytes) -> "SwitchType":
        """Return an instance of this type given a bytestring of its size."""
        raise NotImplementedError()

    def to_bytes(self) -> bytes:
        raise NotImplementedError()

    @classproperty
    def pointer_t(cls):  # pylint: disable=no-self-argument
        """A Pointer type class which points to this type."""
        if not hasattr(cls, "_pointer_t"):
            pointer_class = cls.pointer_class or Pointer
            cls._pointer_t = type(
                cls.__name__+"Pointer",
                (pointer_class,),
                {"dest_type": cls}
            )
        return cls._pointer_t

    def format_reachable_data(self, switch:Switch):
        """Print value for this type and any data reachable through pointers.

        This allows printing of all data reachable from a given data structure,
        following pointers as needed. If a type is not a pointer or doesn't
        contain pointers, this method need not be implemented as __str__ will
        be used by default.
        """
        return str(self)


class AbstractInt(SwitchType):
    """Base class for an integer of any size, signed or unsigned.

    Subclasses need only specify `size` and `signed` class attributes.
    """
    signed:bool

    def __init__(self, value:int):
        self.value = value

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return f"{self.__class__.__name__}({self})"

    def __add__(self, integer):
        c = copy(self)
        c.value += integer
        return c

    @classmethod
    def from_bytes(cls, data:bytes) -> "AbstractInt":
        assert len(data) == cls.size
        value = int.from_bytes(data, byteorder="little", signed=cls.signed)
        return cls(value)

class UInt8(AbstractInt):
    signed = False
    size = 1

class UInt16(AbstractInt):
    signed = False
    size = 2

class UInt32(AbstractInt):
    signed = False
    size = 4

class UInt64(AbstractInt):
    signed = False
    size = 8


class Pointer(UInt64):
    """
    Represents a pointer to a location in memory.

    The main thing you'll want to do with a pointer is dereference it. Use
    `deref()` for this, which actually makes the "peek" call to retrieve the
    value from the switch's memory, hence the need to pass a `Switch` instance
    into `deref()`. You can also integers to pointers just like you can with an
    integer type.

    Usually instead of using this class directly you'll want to use the
    convenience `pointer_t` attribute on any `SwitchType`, which provides a
    pointer to that type. If using this class may be used directly, you must
    specify a type to dereference to when calling `deref()`.

    By default pointers are absolute, but you may specify "main" or "heap" in
    the construtor to indicate that the pointer is for a specific segment of
    memory. Doing so changes the variant of the peek command used when
    dereferencing.
    """
    dest_type: Optional[SwitchType] = None

    def __init__(self, value:int, segment="absolute"):
        super().__init__(value)
        assert segment in {"absolute", "main", "heap"}
        self.segment = segment

    def __str__(self):
        return f"{self.segment}:0x{self.value:08x}"

    def format_reachable_data(self, switch:Switch):
        if self.value == 0 or self.dest_type is None:
            return str(self)
        return self.deref(switch).format_reachable_data(switch)

    @classmethod
    def from_bytes(cls, data) -> "Pointer":
        assert len(data) == 8
        return super(Pointer, cls).from_bytes(data)

    def deref(self, switch:Switch, dest_type:Optional[SwitchType]=None) -> SwitchType:
        dest_type = dest_type or self.dest_type
        if dest_type is None:
            raise ValueError("Specify a type to dereference to")

        data = self.deref_as_bytes(switch, dest_type.size)
        return dest_type.from_bytes(data)

    def deref_as_bytes(self, switch:Switch, size:int) -> bytes:
        if self.segment == "absolute" and self.value == 0:
            raise RuntimeError("Null pointer dereference")
        return switch.peek(self.segment, self.value, size)

    def write_bytes(self, switch:Switch, data:bytes, dest_type:Optional[SwitchType]=None):
        dest_type = dest_type or self.dest_type
        assert dest_type is None or len(data) == dest_type.size
        switch.poke(self.segment, self.value, data)


##################
##### Arrays #####
##################

class AbstractArray(SwitchType):
    """An array of `base_type_cls` types.

    Instances can access the elements of the array like you would a normal
    list, for example `my_array[3]`.

    If you don't need anything fancy, you can make an array type with the
    `make_array_t()` helper function. If you choose to do things manually,
    concrete subclasses must specify `base_type_cls`, `count`, and `size`, and
    the size must be set to `base_type_cls.size * count`.
    """
    #TODO: Make a pointer class for arrays so you can dereference just one (or
    #      more than one) items of the array).
    base_type_cls:SwitchType
    count:int

    def __init__(self, objects:Iterable[SwitchType]):
        self.objects = list(objects)

    def __getitem__(self, index:int):
        return self.objects[index]

    def format_reachable_data(self, switch:Switch):
        formatted_strs = (
            obj.format_reachable_data(switch)
            for obj in self.objects
        )
        return f"[{', '.join(formatted_strs)}]"

    @classmethod
    def from_bytes(cls, data:bytes) -> "AbstractArray":
        assert len(data) == cls.count * cls.base_type_cls.size

        objects = []
        for i in range(cls.count):
            obj = cls.base_type_cls.from_bytes(
                data[i*cls.base_type_cls.size : (i+1)*cls.base_type_cls.size]
            )
            objects.append(obj)

        return cls(objects)

def make_array_t(base_type_cls:Type[SwitchType], count:int):
    return type(
        f"{base_type_cls.__name__}Array",
        (AbstractArray,),
        dict(
            base_type_cls = base_type_cls,
            count = count,
            size = base_type_cls.size * count,
        )
    )


######################
##### Structures #####
######################

class StructPointer(Pointer):
    dest_type:"Struct"

    def deref_field(self, switch:Switch, field_name:str):
        # If we don't check for null pointers here, the same check in the
        # Pointer class won't catch it since value will be field.offset, not 0.
        if self.segment == "absolute" and self.value == 0:
            raise RuntimeError("Null pointer dereference")

        fields = self.dest_type._fields_dict()
        field = fields[field_name]
        field_pointer = Pointer(self.value + field.offset)
        return field_pointer.deref(switch, field.type)

    def format_reachable_data(self, switch:Switch) -> str:
        if self.value == 0:
            return "(null pointer)"
        lines = [
            #str(self)
        ]
        fields = self.dest_type._fields_dict()
        for field_name in fields:
            value = self.deref_field(switch, field_name)
            lines.append(f"{field_name} ({value.__class__.__name__})\n"+indent(
                value.format_reachable_data(switch),
                STRUCT_INDENT
            ))
        return "\n".join(lines)

@dataclass
class StructField:
    name:str
    type:SwitchType
    offset:Optional[int] = None

class Struct(SwitchType):
    fields: Tuple[StructField]
    pointer_class = StructPointer

    Field = StructField

    def __init__(self, data: bytes):
        # pylint: disable=comparison-with-callable
        assert len(data) == self.size
        self.data = data

    def __getitem__(self, field_name:str) -> SwitchType:
        return self.get_field(field_name)

    def get_field(self, field_name:str) -> SwitchType:
        field = self._fields_dict()[field_name]
        return field.type.from_bytes(
            self.data[field.offset : field.offset+field.type.size]
        )

    @classmethod
    def _fields_dict(cls):
        if not hasattr(cls, "_fields_dict_cache"):
            cls._fields_dict_cache = OrderedDict()
            offset = 0
            for field in cls.fields:
                if field.offset is not None:
                    offset = field.offset

                field.offset = offset
                cls._fields_dict_cache[field.name] = field

                offset += field.type.size

        return cls._fields_dict_cache

    @classproperty
    def size(cls):  # pylint: disable=no-self-argument
        # Calculate size by finding highest byte any fields could touch
        return max(
            field.offset + field.type.size
            for field in cls._fields_dict().values()
        )

    @classmethod
    def from_bytes(cls, data:bytes):
        return cls(data)

    @classmethod
    def from_pointer(cls, switch:Switch, pointer:Pointer):
        data = pointer.deref_as_bytes(switch, cls.size)
        return cls(data)
