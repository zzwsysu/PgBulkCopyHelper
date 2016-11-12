# PgBulkCopyHelper

PgBulkCopyHelper 是一个包装了 Npgsql 中 [Binary COPY][1] 方法的类库，用来高效率地把大量数据插入到 [PostgreSQL][2] 数据库当中

PS：这是 PostgreSQL 中用来大批量导入数据的 [COPY][3] 方法的说明

[1]: http://www.npgsql.org/doc/copy.html
[2]: https://www.postgresql.org/
[3]: https://www.postgresql.org/docs/current/static/sql-copy.html

# 开发环境及依赖

* 开发环境为 VS2015
* 用到的第三方库：Npgsql 3.1.8

# 基础用法

1. 假如我们希望把大批量的数据插入到以下的数据表：

	```sql
	CREATE TABLE bld_test (
	    id uuid PRIMARY KEY NOT NULL,
	    tile_x integer,             --x index of the map tile where the building is located
	    tile_y integer,             --y index of the map tile where the building is located
	    bps_gc polygon NOT NULL,    --the bottom points of the building, geodetic coordinates
	    bps_llc polygon NOT NULL,   --the bottom points of the building, Latitude and longitude coordinates
	    cp_gc point NOT NULL,       --the center point of the building, geodetic coordinates
	    cp_llc point NOT NULL,      --the center point of the building, Latitude and longitude coordinates
	    name text,                  --the name of the building
	    bld_floor smallint,         --the number of floors of the building
	    height real                 --the height of building
	);
	```

2. 在项目代码中定义与上表相对应的模型：

	```csharp
	public class SingleBuilding
	    {
	        public Guid id { get; set; }
	        public int tile_x { get; set; }
	        public int tile_y { get; set; }
	        public NpgsqlPolygon bps_gc { get; set; }
	        public NpgsqlPolygon bps_llc { get; set; }
	        public NpgsqlPoint cp_gc { get; set; }
	        public NpgsqlPoint cp_llc { get; set; }
	        public string name { get; set; }
	        public short bld_floor { get; set; }
	        public float height { get; set; }
	    }
	```

3. 根据定义的模型生成一个 PgBulkCopyHelper 实例：

	```csharp
	//函数原型：
	//public PgBulkCopyHelper(string schema, string tableName)
	//或者 public PgBulkCopyHelper(string tableName)
	//在构造 PgBulkCopyHelper 实例时应该指定待会需要插入的数据库中数据表的名称
	PgBulkCopyHelper<SingleBuilding> copyHelper = new PgBulkCopyHelper<SingleBuilding>("public", "bld_test");
	```

4. 初始化对应的数据表，该数据表中的字段名称及其类型与上述模型相对应

	```csharp
	DataTable dataTable = copyHelper.InitDataTable();
	```

5. 将具体的数据，比如某个List\<SingleBuilding\> blds (IEnumerable\<SingleBuilding\>) 填充到数据表中

	```csharp
	//批量填充数据
	List<SingleBuilding> blds = GetBuildings();
	if (blds != null && blds.Count > 0)
	    {
	        copyHelper.FillDataTable(blds, dataTable);
	    }
	
	//亦可一条一条地填充：
	foreach(SingleBuilding bld = GetBuilding())
	{
	    if(bld != null)
	        copyHelper.FillDataTable(bld, dataTable);
	}
	```

6. 填充完之后，就可以一次性快速地插入数据库中

	```csharp
	using (var conn = new NpgsqlConnection(connectionString))
	    {
	        conn.Open();
	        copyHelper.BulkInsert(conn, dataTable);
	    }
	```

如果因内存限值，数据无法一次性填充到一个数据表中，可以使用以下方法：
	```csharp
	//定义每次插入的最大数量限制
	int maxNum = 100000;
	
	//初始化对应的数据表
	DataTable dataTable = copyHelper.InitDataTable();
	
	using (var conn = new NpgsqlConnection(connectionString))
	{
	    conn.Open();
	
	    foreach (List<SingleBuilding> blds in bldsFromSomeWhere())
	    {
	        if (blds != null && blds.Count > 0)
	            //填充数据
	            copyHelper.FillDataTable(blds, dataTable);
	
	        //判断 dataTable 里面的数据量是否已经超过规定最大行数 maxNum
	        if (dataTable.Rows.Count > maxNum)
	        {
	            //如果是，则将 dataTable 里面的数据插入到数据库中
	            copyHelper.BulkInsert(conn, dataTable);
	            //清空 dataTable 中的现有数据
	            dataTable.Clear();
	        }
	    }
	}
	```