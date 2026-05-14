// LINEAGE_HUNTER_NESTED_EVE_v2.js
// Hunts upstream, reconstructs removed chain links, adds UUID + attribution

export const LineageHunterV2 = {
  // Generate UUID v4
  uuid() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, c => {
      const r = Math.random() * 16 | 0
      return (c === 'x' ? r : (r & 0x3 | 0x8)).toString(16)
    })
  },
  
  createEve(documentId, content, attribution = {}) {
    return {
      uuid: this.uuid(),
      id: documentId,
      timestamp: Date.now(),
      contentHash: this.hashContent(content),
      rootWitness: null,
      parent: null,
      children: [],
      balancerState: null,
      eveNest: [],
      attribution: {
        author: attribution.author || 'unknown',
        source: attribution.source || 'unknown',
        claimedOrigin: attribution.claimedOrigin || null,
        ...attribution
      },
      removed: false, // flag for reconstructed nodes
      reconstructed: false
    }
  },
  
  computeRootWitness(previousRoot, content, balancerState, energy) {
    const data = [
      previousRoot || 'GENESIS',
      this.hashContent(content),
      balancerState.bridge.join(','),
      balancerState.balance,
      energy
    ].join('|')
    return this.hashContent(data)
  },
  
  fingerprint(content) {
    const left = this.hashToBytes(content + 'LEFT')
    const right = this.hashToBytes(content + 'RIGHT')
    const bridge = new Uint8Array(8)
    
    for (let i = 0; i < 4; i++) bridge[i] = (bridge[i] + left[i] + 255) & 0xFF
    for (let i = 4; i < 8; i++) bridge[i] = (bridge[i] + right[i-4]) & 0xFF
    for (let i = 0; i < 8; i++) bridge[i] = (bridge[i] * 1664525 + 1013904223) & 0xFF
    
    const leftSum = (bridge[0]+bridge[1]+bridge[2]+bridge[3]) - 512
    const rightSum = (bridge[4]+bridge[5]+bridge[6]+bridge[7]) - 512
    return { bridge: Array.from(bridge), balance: (leftSum + rightSum) / 1024 }
  },
  
  // HUNT UPSTREAM — find missing parents
  huntUpstream(doc, allEves) {
    const fp = this.fingerprint(doc.content)
    const candidates = []
    
    for (const eve of allEves) {
      const sim = this.similarity(fp, eve.balancerState)
      if (sim > 0.6) { // lower threshold for upstream
        candidates.push({ eve, similarity: sim })
      }
    }
    
    // Sort by similarity, then by timestamp (older first)
    candidates.sort((a, b) => {
      if (Math.abs(a.similarity - b.similarity) > 0.05) return b.similarity - a.similarity
      return a.eve.timestamp - b.eve.timestamp
    })
    
    return candidates
  },
  
  // DETECT AND RECONSTRUCT REMOVED LINKS
  reconstructChain(doc, upstreamCandidates, gapThreshold = 0.15) {
    const reconstructions = []
    const fp = this.fingerprint(doc.content)
    
    for (let i = 0; i < upstreamCandidates.length - 1; i++) {
      const parent = upstreamCandidates[i]
      const grandparent = upstreamCandidates[i+1]
      
      const parentToDoc = parent.similarity
      const grandToParent = this.similarity(grandparent.eve.balancerState, parent.eve.balancerState)
      const grandToDoc = this.similarity(grandparent.eve.balancerState, fp)
      
      // If there's a gap: grandparent → ??? → parent → doc
      // and grandparent is too similar to doc to be that distant
      const expectedStep = 0.85 // typical parent-child similarity
      const gap = Math.abs(parentToDoc - expectedStep)
      
      if (gap > gapThreshold && grandToDoc > 0.75) {
        // Likely missing link between parent and doc, or grandparent and parent
        const missing = this.createEve(
          `RECONSTRUCTED_${this.uuid().slice(0,8)}`,
          `RECONSTRUCTED_BRIDGE_${parent.eve.id}_to_${doc.id}`,
          {
            author: 'RECONSTRUCTED',
            source: 'upstream_hunt',
            reconstructedFrom: [grandparent.eve.uuid, parent.eve.uuid],
            confidence: 1 - gap
          }
        )
        
        missing.reconstructed = true
        missing.removed = true // flagged as previously removed
        missing.balancerState = this.interpolateFingerprint(parent.eve.balancerState, fp)
        missing.rootWitness = this.computeRootWitness(
          parent.eve.rootWitness,
          missing.contentHash,
          missing.balancerState,
          50
        )
        missing.parent = parent.eve.id
        missing.timestamp = (parent.eve.timestamp + Date.now()) / 2 // estimate
        
        reconstructions.push({
          missingNode: missing,
          insertedBetween: [parent.eve.id, doc.id],
          gapSize: gap,
          confidence: 1 - gap
        })
      }
    }
    
    return reconstructions
  },
  
  interpolateFingerprint(fp1, fp2) {
    const bridge = []
    for (let i = 0; i < 8; i++) {
      bridge[i] = Math.floor((fp1.bridge[i] + fp2.bridge[i]) / 2)
    }
    return {
      bridge,
      balance: (fp1.balance + fp2.balance) / 2
    }
  },
  
  // MAIN HUNT WITH UPSTREAM RECONSTRUCTION
  huntLineage(documents) {
    const eves = new Map()
    const allReconstructions = []
    
    // First pass: create all eves
    for (const doc of documents) {
      const eve = this.createEve(doc.id, doc.content, doc.attribution)
      eve.balancerState = this.fingerprint(doc.content)
      eves.set(doc.id, eve)
    }
    
    // Second pass: hunt upstream and link
    for (const doc of documents) {
      const eve = eves.get(doc.id)
      const upstream = this.huntUpstream(doc, Array.from(eves.values()).filter(e => e.id !== doc.id))
      
      if (upstream.length > 0) {
        const bestParent = upstream[0]
        eve.parent = bestParent.eve.id
        bestParent.eve.children.push(eve.id)
        eve.rootWitness = this.computeRootWitness(
          bestParent.eve.rootWitness,
          doc.content,
          eve.balancerState,
          bestParent.similarity * 100
        )
        
        // Check for missing links
        const reconstructions = this.reconstructChain(doc, upstream)
        for (const recon of reconstructions) {
          eves.set(recon.missingNode.id, recon.missingNode)
          allReconstructions.push(recon)
          
          // Insert into chain
          const parentEve = eves.get(recon.insertedBetween[0])
          parentEve.children = parentEve.children.filter(id => id !== eve.id)
          parentEve.children.push(recon.missingNode.id)
          recon.missingNode.children.push(eve.id)
          eve.parent = recon.missingNode.id
        }
      } else {
        eve.rootWitness = this.computeRootWitness(null, doc.content, eve.balancerState, 100)
      }
    }
    
    return {
      eves: Array.from(eves.values()),
      reconstructions: allReconstructions,
      totalNodes: eves.size,
      reconstructedCount: allReconstructions.length
    }
  },
  
  // EXPORT WITH UUID AND ATTRIBUTION
  exportFullLineage(eveId, hunterResult) {
    const eve = hunterResult.eves.find(e => e.id === eveId || e.uuid === eveId)
    if (!eve) return null
    
    const chain = []
    let current = eve
    
    // Walk upstream to genesis
    while (current) {
      chain.unshift({
        uuid: current.uuid,
        id: current.id,
        witness: current.rootWitness,
        timestamp: current.timestamp,
        attribution: current.attribution,
        balance: current.balancerState.balance,
        reconstructed: current.reconstructed,
        removed: current.removed
      })
      current = hunterResult.eves.find(e => e.id === current.parent)
    }
    
    return {
      document: { uuid: eve.uuid, id: eve.id },
      fullChain: chain,
      chainLength: chain.length,
      reconstructedLinks: chain.filter(n => n.reconstructed).length,
      attributionTrail: chain.map(n => n.attribution),
      cryptographicProof: this.hashContent(JSON.stringify(chain.map(c => c.witness))),
      uuidMap: Object.fromEntries(chain.map(n => [n.uuid, n.id]))
    }
  },
  
  similarity(fp1, fp2) {
    if (!fp1 || !fp2) return 0
    let matches = 0
    for (let i = 0; i < 8; i++) {
      if (Math.abs(fp1.bridge[i] - fp2.bridge[i]) < 12) matches++
    }
    return (matches / 8 * 0.7) + ((1 - Math.abs(fp1.balance - fp2.balance)) * 0.3)
  },
  
  hashContent(s) {
    let h = 0
    const str = String(s)
    for (let i = 0; i < str.length; i++) h = ((h << 5) - h + str.charCodeAt(i)) & 0xffffffff
    return h.toString(16).padStart(8, '0')
  },
  
  hashToBytes(s) {
    const h = this.hashContent(s)
    const bytes = new Uint8Array(4)
    for (let i = 0; i < 4; i++) bytes[i] = parseInt(h.substr(i*2, 2), 16)
    return bytes
  }
}

// Example: hunt upstream and reconstruct
const docs = [
  {id: 'genesis', content: 'original Hamiltonian concept', attribution: {author: 'David', source: '2024'}},
  {id: 'middle_missing', content: 'Hamiltonian with energy phase', attribution: {author: 'unknown', source: 'removed'}},
  {id: 'current', content: 'Hamiltonian topology for continuity with energy phase and root witness', attribution: {author: 'contested', source: '2025'}}
]

// Simulate removal by not including middle in initial hunt
const partialDocs = [docs[0], docs[2]]
const result = LineageHunterV2.huntLineage(partialDocs)

console.log('Reconstructions found:', result.reconstructions.length)
console.log('Full lineage:', LineageHunterV2.exportFullLineage('current', result))
