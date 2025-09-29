# agent_coordinator.py
class AgentCoordinator:
    """简单的Agent协调器"""
    
    def __init__(self):
        self.agents = {}
        self.conversation_history = []
    
    def register_agent(self, name, agent_func, description):
        """注册Agent"""
        self.agents[name] = {
            'function': agent_func,
            'description': description
        }
    
    def route_question(self, question):
        """路由问题到合适的Agent"""
        question_lower = question.lower()
        
        # 简单的关键词路由
        if any(word in question_lower for word in ['分析', '投资', '股票', '财务']):
            return 'financial'
        elif any(word in question_lower for word in ['数据', '研究', '统计', '市场']):
            return 'research'
        elif any(word in question_lower for word in ['风险', '警告', '问题']):
            return 'risk'
        else:
            return 'general'
    
    def coordinate_response(self, question):
        """协调多个Agent生成回答"""
        # 记录对话历史
        self.conversation_history.append(f"用户: {question}")
        
        # 路由到合适的Agent
        agent_type = self.route_question(question)
        
        if agent_type in self.agents:
            response = self.agents[agent_type]['function'](question)
        else:
            # 默认使用第一个Agent
            first_agent = list(self.agents.values())[0]
            response = first_agent['function'](question)
        
        # 记录响应
        self.conversation_history.append(f"AI ({agent_type}): {response}")
        
        return response, agent_type
    
    def get_conversation_summary(self):
        """获取对话摘要"""
        return "\n".join(self.conversation_history[-6:])  # 返回最近3轮对话

# 使用示例
if __name__ == "__main__":
    # 创建协调器
    coordinator = AgentCoordinator()
    
    # 注册Agent函数
    def financial_agent(question):
        return f"金融分析Agent分析：{question}，建议关注公司基本面和行业趋势。"
    
    def research_agent(question):
        return f"数据研究Agent研究：{question}，数据显示市场前景乐观。"
    
    def risk_agent(question):
        return f"风险评估Agent提醒：{question}，投资有风险，需谨慎决策。"
    
    coordinator.register_agent('financial', financial_agent, '金融分析')
    coordinator.register_agent('research', research_agent, '数据研究') 
    coordinator.register_agent('risk', risk_agent, '风险评估')
    
    # 测试协调器
    questions = [
        "分析苹果公司的股票",
        "提供特斯拉的市场数据",
        "投资有哪些风险",
        "今天天气怎么样"
    ]
    
    for question in questions:
        response, agent_used = coordinator.coordinate_response(question)
        print(f"问题: {question}")
        print(f"使用的Agent: {agent_used}")
        print(f"回答: {response}")
        print("-" * 50)