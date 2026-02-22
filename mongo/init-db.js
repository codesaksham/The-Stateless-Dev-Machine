const databases = process.env.MONGO_MULTIPLE_DATABASES || '';
if (databases) {
    const dbList = databases.split(',').map(db => db.trim());
    dbList.forEach(dbName => {
        const targetDb = db.getSiblingDB(dbName);
        targetDb.createCollection('init'); // MongoDB creates DB on first collection creation
        console.log(`Created database: ${dbName}`);
    });
}
