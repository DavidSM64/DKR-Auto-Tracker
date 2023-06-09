/* This file contains helper functions for drawing a basic map on a html canvas */

const HUB_LEVELS = ["OW", "DD", "SI", "SM", "DF", "FFL"]

class MapDrawer {
    constructor(width = 500, height = 500) {
        this.canvas = document.createElement('canvas');
        this.canvas.width = width;
        this.canvas.height = height;
        document.body.appendChild(this.canvas);
        this.ctx = this.canvas.getContext('2d');
        this.nodes = {}
    }
    
    clear() {
        this.nodes = {}
        this.update({})
    }
    
    update(mapData) {
        // Merge this.nodes with mapData
        let mapDataKeys = Object.keys(mapData)
        for(let mapKey of mapDataKeys) {
            if(!(mapKey in this.nodes)) {
                this.nodes[mapKey] = mapData[mapKey];
                continue;
            }
            for (let mapEntry of mapData[mapKey]) {
                if(!this.nodes[mapKey].includes(mapEntry)) {
                    this.nodes[mapKey].push(mapEntry);
                }
            }
        }
    
        this.DoneNodes = []
        this.nodePositions = {}
        
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        let x = this.canvas.width / 2;
        let y = this.canvas.height / 2;
        this._drawNodeAndChildren("OW", x, y);
        this._drawNodeArrows();
    }
    
    _drawNodeArrows() {
        let keys = Object.keys(this.nodes);
        for (let fromNode of keys) {
            let toNodes = this.nodes[fromNode];
            let fromNodeProp = this.nodePositions[fromNode];
            for (let toNode of toNodes) {
                let toNodeProp = this.nodePositions[toNode];
                this._drawArrowBetweenCircles(
                    fromNodeProp.x, fromNodeProp.y, fromNodeProp.r, 
                    toNodeProp.x, toNodeProp.y, toNodeProp.r
                );
            }
        }
    }
    
    _getUnfinishedNodes(nodes) {
        let out = []
        for (let i = 0; i < nodes.length; i++) {
            if (!this.DoneNodes.includes(nodes[i])) {
                out.push(nodes[i]);
            }
        }
        return out;
    }
    
    _drawNodeAndChildren(nodeName, x, y, textSize=24, r=120, angle=0) {
        if (this.DoneNodes.includes(nodeName)) {
            return;
        }
        this.DoneNodes.push(nodeName);
        if((nodeName in this.nodes)) {
            let numChildren = this.nodes[nodeName].length;
            if(numChildren > 0) {
                let notDoneNodes = this._getUnfinishedNodes(this.nodes[nodeName]);
                let pos = this._positionNodesCircular(x, y, r, angle, notDoneNodes.length);
                
                for(let i = 0; i < notDoneNodes.length; i++) {
                    let cx = pos[i].x;
                    let cy = pos[i].y;
                    this._drawNodeAndChildren(notDoneNodes[i], cx, cy, 
                        Math.trunc(textSize * 0.75), Math.trunc(r * 0.5), angle + 15);
                    
                }
            }
        }
        
        let nodeR = this._drawNode(nodeName, x, y, textSize);
        this.nodePositions[nodeName] = {
            x: x,
            y: y,
            r: nodeR
        }
    }
    
    _positionNodesCircular(centerX, centerY, radius, angle, numNodes) {
        let positions = [];
        let angleStep = 2 * Math.PI / numNodes;
        for (let i = 0; i < numNodes; i++) {
            let x = centerX + radius * Math.cos(angle);
            let y = centerY + radius * Math.sin(angle);
            positions.push({x: x, y: y});
            angle += angleStep;
        }
        return positions;
}

    
    _drawArrow(fromx, fromy, tox, toy, color='red') {
        let headlen = 10; // length of head in pixels
        let dx = tox - fromx;
        let dy = toy - fromy;
        let angle = Math.atan2(dy, dx);
        this.ctx.beginPath();
        this.ctx.strokeStyle = color;
        this.ctx.moveTo(fromx, fromy);
        this.ctx.lineTo(tox, toy);
        this.ctx.lineTo(tox - headlen * Math.cos(angle - Math.PI / 6), toy - headlen * Math.sin(angle - Math.PI / 6));
        this.ctx.moveTo(tox, toy);
        this.ctx.lineTo(tox - headlen * Math.cos(angle + Math.PI / 6), toy - headlen * Math.sin(angle + Math.PI / 6));
        this.ctx.stroke()
    }

    _drawNode(text, x, y, textSize=30, ovalColor='black', textColor='white') {
        this.ctx.font = textSize + "px Courier New";
        this.ctx.textAlign = "center";
        let textLength = this.ctx.measureText(text).width;
        this.ctx.font = textSize + "px Arial";
        let r = (textLength + textSize) / 2;
        this.ctx.beginPath();
        this.ctx.fillStyle = ovalColor;
        this.ctx.arc(x, y, r, 0, 2 * Math.PI, false);
        this.ctx.fill();
        this.ctx.fillStyle = textColor;
        this.ctx.fillText(text, x, y + (textSize/(2*Math.sqrt(2))));
        return r;
    }

    _drawArrowBetweenCircles(circle0X, circle0Y, circle0Radius, circle1X, circle1Y, circle1Radius, arrowColor='red') {
        // Calculate the angle between the centers of the two circles
        let angle = Math.atan2(circle1Y - circle0Y, circle1X - circle0X);

        // Calculate the starting point (x0,y0) of the arrow on the edge of the first circle
        let x0 = circle0X + Math.cos(angle) * circle0Radius;
        let y0 = circle0Y + Math.sin(angle) * circle0Radius;

        // Calculate the ending point (x1,y1) of the arrow on the edge of the second circle
        let x1 = circle1X - Math.cos(angle) * circle1Radius;
        let y1 = circle1Y - Math.sin(angle) * circle1Radius;

        // Draw the arrow using the provided drawArrow function
        this._drawArrow(x0, y0, x1, y1, arrowColor);
    }
}