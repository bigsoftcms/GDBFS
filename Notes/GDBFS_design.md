# GDBFS逻辑组织结构设计   
### Version  1.0


### 零. 概要思想

我们的目标是一个知道我们要什么，以及能预测我们要什么的文件系统。所以可以这么说，人在内心中对于文件有一套自己的看法。这个看法包括了对哪些文件具有哪些属性，我习惯用什么属性去搜索什么文件，我访问文件或者搜索属性有一定的先后顺序。
所以，我们想用我们这张文件系统组织逻辑图，来逼近用户心中的那张图。所以我们的图不是一成不变的，而是随时在动态变化的。可以类比脑神经间记忆增强以及记忆忘却的关系。
但是我们又不希望一些大家公认的关系因为个人习惯的关系而被忘掉，比如一个用户习惯用pdf这个属性来搜索一本教材，但是我们并不想忘记这个教材同样具有学习用途这个属性。所以一些公认的关系不能被删去。
基于此，我目前设想的操作界面是：系统推荐给用户许多节点（包括文件与属性节点），用户选择文件节点的话就打开文件，用户选择属性节点的话就继续进一步推荐。
详细结构，逻辑，以及算法如下。


#### 结构

节点分为两种，文件节点与属性节点。

	1. 文件节点：
	{ 
		Label: 
		{
		    File
		}
		Property:
		{
		    
			name, length, mtime, mtime, atime, id, key_to_find_in_mongoDB …
		}
			
	}
	

	2. 属性节点：
	{
		 Property：
		    Attribute, 如 学习用途 我喜欢的 欧美流行 等等
		 Label：
			属性层的名字，如 用途层 自定义层 音乐层 等等
			
	}





关系分为两种，静态关系以及动态关系。
		
	1. Static Relationship：
	{
		Type:
			Static
		Property:
			Distance ( integer )
	}

	2. Dynamic Relationship：
	{
		Type:
			Dynamic
		Property:
			Distance ( integer )
	}

关系之所以区分两类，是因为希望静态关系不被删掉，而动态关系可以随使用过程而增加和减少。
	动态关系存在于：
		1. 文件夹间的从属关系。这是当然不能随意删掉的。
		2. 每一层属性层上的基本公认关系。这是我们不希望被删掉的。


### 二. 操作(大概）
	
目前的想法是，最重要也是最有特色的一个操作是 `stimulate(node_id, max_distance, relation_type, target_type)`，用来找出输入节点周围一定距离内的节点。含义是用户想到这个节点时，用户心中可能是想要另外一些节点。我们想要我们找出来的跟用户想要的差不多。  



### 三. 智能
	
智能分为两种。
	需要提的是，只能方面不影响我们前面基本框架的搭建，但是这块内容我们应该事先要知道大概怎么做，这将引导我们基本框架的搭建。
1. 一种用来给文件添加属性。这种不是我们的重点，也不用在初步阶段考虑。现在已有各种成熟的手段与框架，后期加入我们的文件系统不难。
	
2. 另一种是文件组织逻辑对用户习惯的学习，这个需要在设计阶段考虑。目前我的想法如下：
	
	目的是学习用户习惯，以及为用户推荐合适的节点。
	如果我们坐在节点旁，不区分文件节点与属性节点，看这些用户操作，其实就是用户不断的在这些节点间跳来跳去（搜索属性，点击下一个属性，点击文件节点，点击文件节点。。。）这些都是对节点的访问。
	那么用户的这一串访问序列有没有什么规律，如何做到human intent prediction？这是我们要做的。
	那么这样，不论用户执行的是属性搜索，节点访问，文件打开，我们都对这个节点调用 stimulate，然后从这个节点（或这几个节点）出发，找到周围在一定距离内的目的节点，根据距离远近，作出推荐（对于多个出发节点的情况，一个简单的做法可以是优先共同目的节点，一个复杂点但是更合理的做法需要对这些目的节点重新排序，不在此细说）。然后将用户下一步的选择视为反馈进行online learning。

	目前，一个简单的算法如下：它能在一定假设下收敛到最优解。
	目前我们只需要知道算法思想，具体算法可以后续再改。（目前我觉得HMM可能会是我们想要的方法）。
		

### 四. 细节设计


* 每个节点都要有不同的ID，而节点名可以重复
* 节点名可以重复，但是在传统文件层的文件夹节点（由传统文件系统创造的文件夹）下要保证文件名不重复，跟传统文件系统的命名规则一样。传统文件系统不能区分文件名相同时谁是谁。而我们的客户端可以做到这点。
* 目前设计的是由五个py文件组成。`neo4j_support`提供对neo4j的基本操作的包装，包括对高级搜索的支持。`mongoDB_support`提供对 mongoDB 最基本的操作，包括对文件的基本操作，如 read write exist等操作。`GDBFS`对两个数据库做一个封装，提供我们文件系统最基本的操作。`GDBFS_fuse`调用`GDBFS`模块来接驳fuse，`GDBFS_client`调用`GDBFS`模块来实现客户端界面操作。

