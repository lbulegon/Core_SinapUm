MERGE (m:Agent {id:"motoboy_1", type:"Motoboy", name:"João"})
MERGE (r:Agent {id:"rest_1", type:"Restaurante", name:"Mister Dog"})
MERGE (p:Object {id:"pedido_100", type:"Pedido", status:"novo"})
MERGE (loc:Place {id:"loc_1", city:"Santa Maria"})

MERGE (m)-[:WORKS_FOR {layer:"operational", ts: datetime()}]->(r)
MERGE (p)-[:BELONGS_TO {layer:"operational", ts: datetime()}]->(r)
MERGE (m)-[:LOCATED_IN {layer:"spatial", ts: datetime()}]->(loc)

CREATE (e:Event {id:"ev_1", kind:"pedido_criado", ts: datetime(), layer:"temporal"})
MERGE (e)-[:ABOUT {layer:"temporal"}]->(p);
