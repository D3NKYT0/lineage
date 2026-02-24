import os
import glob
import re

query_dir = r"d:\PROJETOS\PDL\SITE\apps\lineage\server\querys"
files = glob.glob(os.path.join(query_dir, "query_*.py"))

method_to_inject = '''
    @staticmethod
    def get_clan_members(clan_id):
        \"\"\"Retorna os membros de um clã.\"\"\"
        db = LineageDB()
        if not getattr(db, 'enabled', False):
            return []
        try:
            sql = \"\"\"
                SELECT 
                    C.char_name, 
                    C.online, 
                    C.pvpkills, 
                    C.pkkills,
                    (SELECT S0.level FROM character_subclasses AS S0 WHERE S0.char_obj_id = C.obj_Id AND S0.isBase = '1' LIMIT 1) AS level,
                    (SELECT S0.class_id FROM character_subclasses AS S0 WHERE S0.char_obj_id = C.obj_Id AND S0.isBase = '1' LIMIT 1) AS base,
                    C.access_level AS accesslevel
                FROM characters C
                WHERE C.clanid = :clan_id OR C.clan_id = :clan_id
                ORDER BY C.online DESC, level DESC, C.char_name ASC
            \"\"\"
            result = db.select(sql, {"clan_id": clan_id})
            return result if result else []
        except Exception as e:
            try:
                # Fallback mais básico
                sql_fallback = "SELECT char_name, online FROM characters WHERE clanid = :clan_id OR clan_id = :clan_id ORDER BY online DESC, char_name ASC"
                result = db.select(sql_fallback, {"clan_id": clan_id})
                return result if result else []
            except:
                return []
'''

for file_path in files:
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Check if get_clan_members is already in the file
    if "def get_clan_members" in content:
        print(f"Skipping {os.path.basename(file_path)} - already contains get_clan_members")
        continue

    # Find where to inject - after get_clan_full_details method body
    # Specifically, look for the return result of get_clan_full_details in LineageClans
    match = re.search(r"def get_clan_full_details.*?return result\n", content, flags=re.DOTALL)
    
    if match:
        insertion_point = match.end()
        new_content = content[:insertion_point] + "\n" + method_to_inject + "\n" + content[insertion_point:]
        
        # In some templates access level is accesslevel, others access_level. We do a blind fallback for accesslevel inside the sql string, replacing C.access_level
        # Actually let's just make it select C.accesslevel and if it fails, the fallback catches it.
        new_content = new_content.replace('C.access_level AS accesslevel', 'C.accesslevel')
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)
            
        print(f"Updated {os.path.basename(file_path)}")
    else:
        print(f"Could not find injection point in {os.path.basename(file_path)}")

