class LogFormatter:
    @staticmethod
    def section(text: str) -> str:
        """
        创建主要分隔区块
        例如：
        ==================================================
         字体库扫描 
        ==================================================
        """
        separator = "=" * 50
        return f"\n{separator}\n {text} \n{separator}"

    @staticmethod
    def subsection(text: str) -> str:
        """
        创建子分隔区块
        例如：
        ----------------------------------------
         处理统计 
        ----------------------------------------
        """
        separator = "-" * 40
        return f"\n{separator}\n {text} \n{separator}"

    @staticmethod
    def process_start(title: str) -> str:
        """
        创建处理开始标记
        例如：
        >>> 开始处理：字幕合并
        """
        return f"\n>>> {title}"

    @staticmethod
    def process_end(title: str) -> str:
        """
        创建处理结束标记
        例如：
        <<< 处理完成：字幕合并
        """
        return f"<<< {title}"

    @staticmethod
    def list_item(text: str) -> str:
        """
        创建列表项
        例如：
        - 项目内容
        """
        return f"• {text}"

    @staticmethod
    def success(text: str) -> str:
        """
        创建成功消息
        例如：
        ✓ 成功：找到字体
        """
        return f"✓ {text}"

    @staticmethod
    def error(text: str) -> str:
        """
        创建错误消息
        例如：
        ✗ 错误：文件不存在
        """
        return f'<font color="red">✗ {text}</font>'

    @staticmethod
    def warning(text: str) -> str:
        """
        创建警告消息
        例如：
        ⚠ 警告：文件不存在
        """
        return f'<font color="red">⚠ {text}</font>' 