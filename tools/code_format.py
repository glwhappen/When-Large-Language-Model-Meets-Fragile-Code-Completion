import re


def test_remove_copy_code(code: str = 'typescript\nCopy code\n            if (compare <= 0 && values[i'):
    """
    去除复制代码
    :param code:
    :return:
    """
    pos = code.find('Copy code')
    if pos != -1:
        code = code[pos + len('Copy code'):]
    return code


def get_function(code_snippet):
    last_function_match = re.findall(r'((?:@[\w\s]+)?public\s+\w+\s+\w+\(.*?\)\s*\{.*?\n\s*\}|private\svoid\s\w+\(.*?\)\s*\{.*?\n\s*\})', code_snippet, re.DOTALL)

    # Extracting the last complete function or return an empty string if none found
    last_function = last_function_match[-1] if last_function_match else ""
    return last_function


if __name__ == '__main__':
    test = """
    
        public EnumSerializer(EnumValues v) {
        this(v, null);
    }

    public EnumSerializer(EnumValues v, Boolean serializeAsIndex)
    {
        super(v.getEnumClass(), false);
        _values = v;
        _serializeAsIndex = serializeAsIndex;
    }

    /**
     * Factory method used by {@link com.fasterxml.jackson.databind.ser.BasicSerializerFactory}
     * for constructing serializer instance of Enum types.
     * 
     * @since 2.1
     */
    @SuppressWarnings("unchecked")
    public static EnumSerializer construct(Class<?> enumClass, SerializationConfig config,
            BeanDescription beanDesc, JsonFormat.Value format)
    {
        /* 08-Apr-2015, tatu: As per [databind#749], we can not statically determine
         *   between name() and toString(), need to construct `EnumValues` with names,
         *   handle toString() case dynamically (for example)
         */
        EnumValues v = EnumValues.constructFromName(config, (Class<Enum<?>>) enumClass);

    """
    print(get_function(test))