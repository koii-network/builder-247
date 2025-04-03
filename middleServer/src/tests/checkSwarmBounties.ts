import { prometheusDB } from '../services/database/database';
import SwarmBounty from '../models/SwarmBounties';

async function checkSwarmBounties() {
    try {
        // Check raw collection
        const collection = prometheusDB.collection('swarmbounties');
        const count = await collection.countDocuments({});
        console.log('Raw collection count:', count);

        // Check using model
        const bounties = await SwarmBounty.find({});
        console.log('Model find count:', bounties.length);

        // Check specific query
        const docSummarizerBounties = await SwarmBounty.find({ swarmType: 'document-summarizer' });
        console.log('Document summarizer bounties count:', docSummarizerBounties.length);

        // Log first few documents
        const docs = await collection.find({}).limit(5).toArray();
        console.log('First few documents:', JSON.stringify(docs, null, 2));
    } catch (error) {
        console.error('Error checking swarm bounties:', error);
    } finally {
        process.exit(0);
    }
}

checkSwarmBounties(); 