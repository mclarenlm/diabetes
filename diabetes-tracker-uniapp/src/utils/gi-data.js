export const GI_DATA = [
    // 主食类
    {name:'白米饭', gi:83, cat:'主食'}, {name:'糙米饭', gi:50, cat:'主食'},
    {name:'白粥', gi:90, cat:'主食'}, {name:'小米粥', gi:62, cat:'主食'},
    {name:'燕麦片', gi:55, cat:'主食'}, {name:'即食燕麦', gi:79, cat:'主食'},
    {name:'白面包', gi:75, cat:'主食'}, {name:'全麦面包', gi:50, cat:'主食'},
    {name:'馒头', gi:88, cat:'主食'}, {name:'面条', gi:82, cat:'主食'},
    {name:'荞麦面', gi:59, cat:'主食'}, {name:'红薯', gi:54, cat:'主食'},
    {name:'紫薯', gi:48, cat:'主食'}, {name:'土豆(煮)', gi:66, cat:'主食'},
    {name:'土豆泥', gi:87, cat:'主食'}, {name:'玉米', gi:55, cat:'主食'},
    {name:'糯米饭', gi:87, cat:'主食'}, {name:'藜麦', gi:53, cat:'主食'},
    {name:'意大利面', gi:45, cat:'主食'}, {name:'饺子', gi:60, cat:'主食'},
    // 水果类
    {name:'苹果', gi:36, cat:'水果'}, {name:'香蕉', gi:52, cat:'水果'},
    {name:'熟香蕉', gi:62, cat:'水果'}, {name:'橙子', gi:43, cat:'水果'},
    {name:'葡萄', gi:43, cat:'水果'}, {name:'西瓜', gi:72, cat:'水果'},
    {name:'草莓', gi:40, cat:'水果'}, {name:'猕猴桃', gi:52, cat:'水果'},
    {name:'梨', gi:38, cat:'水果'}, {name:'桃子', gi:42, cat:'水果'},
    {name:'樱桃', gi:22, cat:'水果'}, {name:'柚子', gi:25, cat:'水果'},
    {name:'菠萝', gi:66, cat:'水果'}, {name:'芒果', gi:55, cat:'水果'},
    {name:'哈密瓜', gi:65, cat:'水果'}, {name:'木瓜', gi:58, cat:'水果'},
    // 蔬菜类
    {name:'西兰花', gi:15, cat:'蔬菜'}, {name:'菠菜', gi:15, cat:'蔬菜'},
    {name:'生菜', gi:15, cat:'蔬菜'}, {name:'黄瓜', gi:15, cat:'蔬菜'},
    {name:'番茄', gi:30, cat:'蔬菜'}, {name:'胡萝卜(生)', gi:35, cat:'蔬菜'},
    {name:'胡萝卜(熟)', gi:85, cat:'蔬菜'}, {name:'白菜', gi:15, cat:'蔬菜'},
    {name:'茄子', gi:15, cat:'蔬菜'}, {name:'芹菜', gi:15, cat:'蔬菜'},
    {name:'豆芽', gi:20, cat:'蔬菜'}, {name:'蘑菇', gi:15, cat:'蔬菜'},
    {name:'洋葱', gi:10, cat:'蔬菜'}, {name:'青椒', gi:15, cat:'蔬菜'},
    // 豆类/蛋/奶
    {name:'豆腐', gi:15, cat:'豆奶蛋'}, {name:'豆浆', gi:15, cat:'豆奶蛋'},
    {name:'黄豆', gi:18, cat:'豆奶蛋'}, {name:'绿豆', gi:27, cat:'豆奶蛋'},
    {name:'红豆', gi:23, cat:'豆奶蛋'}, {name:'鹰嘴豆', gi:28, cat:'豆奶蛋'},
    {name:'牛奶', gi:27, cat:'豆奶蛋'}, {name:'酸奶(无糖)', gi:35, cat:'豆奶蛋'},
    {name:'鸡蛋', gi:30, cat:'豆奶蛋'}, {name:'奶酪', gi:30, cat:'豆奶蛋'},
    // 肉类/鱼
    {name:'鸡胸肉', gi:0, cat:'肉鱼'}, {name:'牛肉', gi:0, cat:'肉鱼'},
    {name:'猪肉', gi:0, cat:'肉鱼'}, {name:'羊肉', gi:0, cat:'肉鱼'},
    {name:'鲈鱼', gi:0, cat:'肉鱼'}, {name:'三文鱼', gi:0, cat:'肉鱼'},
    {name:'虾', gi:0, cat:'肉鱼'}, {name:'带鱼', gi:0, cat:'肉鱼'},
    // 零食/其他
    {name:'坚果(混合)', gi:15, cat:'零食'}, {name:'核桃', gi:15, cat:'零食'},
    {name:'杏仁', gi:15, cat:'零食'}, {name:'花生', gi:14, cat:'零食'},
    {name:'黑巧克力', gi:23, cat:'零食'}, {name:'饼干', gi:70, cat:'零食'},
    {name:'蛋糕', gi:80, cat:'零食'}, {name:'蜂蜜', gi:58, cat:'零食'},
    {name:'白糖', gi:65, cat:'零食'}, {name:'果汁', gi:68, cat:'零食'},
    {name:'可乐', gi:63, cat:'零食'}, {name:'啤酒', gi:66, cat:'零食'},
    {name:'爆米花', gi:72, cat:'零食'}, {name:'薯片', gi:75, cat:'零食'},
];

export function giColor(gi) {
    if (gi === 0) return '#718096'
    if (gi < 55) return '#38a169'
    if (gi <= 70) return '#d69e2e'
    return '#e53e3e'
}
export function giLabel(gi) {
    if (gi === 0) return '无GI'
    if (gi < 55) return '低GI ✅'
    if (gi <= 70) return '中GI ⚠️'
    return '高GI ❌'
}
