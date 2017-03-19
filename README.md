# PgBulkCopyHelper

PgBulkCopyHelper 是一个包装了 Npgsql 中 [Binary COPY][1] 方法的类库，用来高效率地把大量数据插入到 [PostgreSQL][2] 数据库当中

PS：这是 PostgreSQL 中用来大批量导入数据的 [COPY][3] 方法的说明

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

3. 根据定义的模型生成一个 PgBulkCopyHelper 实例（[数据类型映射][4]）：

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
        //记得要把最后一次的数据插入
        copyHelper.BulkInsert(conn, dataTable);
    }
    ```

7. 假如有如下数据表以及对应的数据模型

    数据表结构：

    ```sql
    CREATE TABLE bld_test (
        id SERIAL PRIMARY KEY NOT NULL,
        name TEXT,
        floor INTEGER,
        footprints_gcj02 geometry(POLYGON, 0),
        footprints_proj_gcj02 geometry(POLYGON, 2362),
        footprints_wgs84 geometry(POLYGON, 4326),
        footprints_proj_wgs84 geometry(POLYGON, 2362),
        z_gcj02 INTEGER,
        x_gcj02 INTEGER,
        y_gcj02 INTEGER
    );
    ```

    对应数据模型：

    ```csharp
    public class SingleBuilding
    {
        public string name { get; set; }
        public int floor { get; set; }
        public PostgisPolygon footprints_gcj02 { get; set; }
        public PostgisPolygon footprints_proj_gcj02 { get; set; }
        public PostgisPolygon footprints_wgs84 { get; set; }
        public PostgisPolygon footprints_proj_wgs84 { get; set; }
        public int z_gcj02 { get; set; }
        public int x_gcj02 { get; set; }
        public int y_gcj02 { get; set; }
    }
    ```

    可以发现，数据模型中的属性并不能完全覆盖数据表中的字段。
    该情况在v1.1.0之后的版本能够正常工作， PgBulkCopyHelper 会将 SingleBuilding 中所有的数据填充到对应的的数据表的字段中。
    当然， SingleBuilding 中不存在的属性在 bld_test 中不能为 null

[1]: http://www.npgsql.org/doc/copy.html
[2]: https://www.postgresql.org/
[3]: https://www.postgresql.org/docs/current/static/sql-copy.html
[4]: http://www.npgsql.org/doc/types.html