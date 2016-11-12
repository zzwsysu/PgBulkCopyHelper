using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

using PgBulkCopyHelper;
using NpgsqlTypes;
using System.Reflection;

namespace Test_proj
{
    class Program
    {
        static void Main(string[] args)
        {
            var test = new PgBulkCopyHelper<SingleBuilding>("bld_amap_gzmain");

            foreach (string pName in test.PropNames)
            {
                Console.WriteLine("name: {0},\t\ttype: {1}", pName, test.PropInfo[pName]);
            }
        }
    }

    public class SingleBuilding
    {
        //创建数据表的SQL语句如下：
        /*
        CREATE TABLE bld_amap_gzmain (
            id uuid PRIMARY KEY NOT NULL,
            tile_x integer,             --x index of the map tile where the building is located
            tile_y integer,             --y index of the map tile where the building is located
            bps_gc polygon NOT NULL,    --the points of the bottom outline of the building, geodetic coordinates
            bps_llc polygon NOT NULL,   --the points of the bottom outline of the building, Latitude and longitude coordinates
            cp_gc point NOT NULL,       --the center point of the building, geodetic coordinates
            cp_llc point NOT NULL,      --the center point of the building, Latitude and longitude coordinates
            name text,
            bld_floor smallint,         --the number of floors of the building
            height real                 --the height of building
        );
        */

        public Guid id { get; set; }
        public int? tile_x { get; set; }
        public int? tile_y { get; set; }
        public NpgsqlPolygon bps_gc { get; set; }
        public NpgsqlPolygon bps_llc { get; set; }
        public NpgsqlPoint cp_gc { get; set; }
        public NpgsqlPoint cp_llc { get; set; }
        public string name { get; set; }
        public short? bld_floor { get; set; }
        public float? height { get; set; }
    }
}
